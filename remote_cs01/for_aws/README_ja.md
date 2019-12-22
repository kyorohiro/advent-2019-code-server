これは、2019年 code-server に Advent Calender の 第13日目の記事です。

前回に続き、EC2 Instance を 立ち上げたいと思います。


目次
[ローカル環境篇 1日目](https://qiita.com/kyorohiro/items/35bab591cd4a6b975c80) 
[オンライン環境篇 1日目 作業環境を整備する](https://qiita.com/kyorohiro/items/603d6ee693fc2300079e)
[オンライン環境篇 2日目 仮想ネットワークを作成する](https://qiita.com/kyorohiro/items/6f2452ec2a2fe3640979)
[オンライン環境篇 3日目 Boto3 で EC2 インスタンスを立ち上げる](https://qiita.com/kyorohiro/items/32c9b7f9ebfccbeb6ac5)
[オンライン環境篇 4日目 Code-Serverをクラウドで動かしてみる](https://qiita.com/kyorohiro/items/3701fc97f61e94c5ba95)
オンライン篇 5日目 Docker環境を構築してアレコレ
オンライン篇 6日目 簡単な起動アプリを作成してみよう
...
オンライン篇 .. Coomposeファイルで構築
オンライン篇 .. K8Sを試してみる
...
魔改造篇 


# EC2 とは
https://aws.amazon.com/ec2/

EC2はAWSが提供している仮想サーバーです。秒単位で課金されるサーバーです。Linuxを自由に利用できます。

# ネットワークを構築しよう!!

EC2 Instance を 立ち上げる前に、ネットワークを構築しましょう。デフォルトのを利用しても良いですが、せっかくですのでお試しください。

## 仮想ネッワーク を 作成
https://aws.amazon.com/vpc/

まずは、仮想ネットワークを作成します。。

```Python
import boto3
from boto3_type_annotations import ec2

instance_name= "advent-code-server"

ec2client:ec2.Client = boto3.client("ec2")
res = ec2client.create_vpc(CidrBlock='10.1.0.0/16')
print("{}".format(res))
```

https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.create_vpc

これだけで、作成できます。
CidrBlockは割り振るIPを意味しています。
今回の場合だと
10.1.0.0 から 10.1.255.255 までの IPを、利用できます。


管理しやすいように、TAGを、打っておきましょう

```Python
import boto3
from boto3_type_annotations import ec2
from typing import Dict, List 

instance_name= "advent-code-server"

def attach_tag(id:str):
    res = ec2client.create_tags(Resources=[id], Tags=[{"Key": "Name", "Value": instance_name}])
    print("{}".format(res))

def create_vpc():
    print(">>> CREATE VPC")
    res = ec2client.create_vpc(CidrBlock='10.1.0.0/16')
    print("{}".format(res))
    vpc_id = res['Vpc']['VpcId']
    attach_tag(vpc_id)
    return vpc_id
```


はい、出来ました。`create_vpc()` を Callすると 仮想ネットワークを作成出来ます。


## 仮想ネッワーク を 削除

作成したものを、いつでも削除できるようにしておく必要があります。
削除するスクリプトを書いてみましょう

```Python
def rm_vpc():
    print(">>> Delete vpcs")
    res = ec2client.describe_vpcs(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for vpc in res["Vpcs"]:
        res = ec2client.delete_vpc(VpcId=vpc['VpcId'])
        print("{}".format(res))
```

TagをAttachしているので、削除が簡単です。
Tagに紐づく VPC を探して、見つかったVPCを削除します。


## ここまでを試してみましょう。

```Python
import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
from typing import Dict, List 

instance_name= "advent-code-server"
ec2client:ec2.Client = boto3.client("ec2")

def attach_tag(id:str):
    res = ec2client.create_tags(Resources=[id], Tags=[{"Key": "Name", "Value": instance_name}])
    print("{}".format(res))

def create_vpc():
    print(">>> CREATE VPC")
    res = ec2client.create_vpc(CidrBlock='10.1.0.0/16')
    print("{}".format(res))
    vpc_id = res['Vpc']['VpcId']
    attach_tag(vpc_id)
    return vpc_id

def delete_vpc():
    print(">>> Delete vpcs")
    res = ec2client.describe_vpcs(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for vpc in res["Vpcs"]:
        res = ec2client.delete_vpc(VpcId=vpc['VpcId'])
        print("{}".format(res))
    
if __name__ == "__main__":
    create_vpc()
    rm_vpc()

```

作成して、削除するだけの、コードができました!!


```
　　　　 ∧＿∧
　／＼（　・∀・）／ヽ
（ ●　と　　　つ　● ）     .. 休憩 ..
　＼/⊂、　 　ノ　＼ノ
　　　　　し’
````

## Internet Gateway を 追加
https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html

VPCはこのままだと、Internet と接続できません。接続するための 入り口(Gateway) を設定しましょう。

```Python
def create_gateway(vpc_id:str):
    print(">>> CREATE GATEWAY")
    res = ec2client.create_internet_gateway()
    print("{}".format(res))
    gateway_id = res['InternetGateway']['InternetGatewayId']
    attach_tag(gateway_id)

    print(">>> ATTACH GATEWAY")
    res = ec2client.attach_internet_gateway(InternetGatewayId=gateway_id,VpcId=vpc_id)
    print("{}".format(res))
```

Gatewayを作成して、VPCに関連づけています。


## Internet Gateway を 削除

では、削除するコードを書きましょう。

```Python
def delete_gateway():
    print(">> Detach Gateway")
    res = ec2client.describe_vpcs(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for vpc in res["Vpcs"]:
        res = ec2client.describe_internet_gateways(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
        print("{}".format(res))
        for gateway in res['InternetGateways']:
            res = ec2client.detach_internet_gateway(InternetGatewayId=gateway['InternetGatewayId'],VpcId=vpc['VpcId'])
            print("{}".format(res))

    print(">> Delete Gateway")
    res = ec2client.describe_internet_gateways(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for gateway in res['InternetGateways']:
        res = ec2client.delete_internet_gateway(InternetGatewayId=gateway['InternetGatewayId'])
        print("{}".format(res))
```

削除するためには、VPCの関連付けを外す必要があります。
あとは、同じように、Tagに紐づく データーを探して削除していきます。

## ここまでを試してみましょう。

```Python
import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
from typing import Dict, List 

instance_name= "advent-code-server"
ec2client:ec2.Client = boto3.client("ec2")



def attach_tag(id:str):
    res = ec2client.create_tags(Resources=[id], Tags=[{"Key": "Name", "Value": instance_name}])
    print("{}".format(res))

def create_vpc():
    print(">>> CREATE VPC")
    res = ec2client.create_vpc(CidrBlock='10.1.0.0/16')
    print("{}".format(res))
    vpc_id = res['Vpc']['VpcId']
    attach_tag(vpc_id)
    return vpc_id

def delete_vpc():
    print(">>> Delete vpcs")
    res = ec2client.describe_vpcs(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for vpc in res["Vpcs"]:
        res = ec2client.delete_vpc(VpcId=vpc['VpcId'])
        print("{}".format(res))
    
def create_gateway(vpc_id:str):
    print(">>> CREATE GATEWAY")
    res = ec2client.create_internet_gateway()
    print("{}".format(res))
    gateway_id = res['InternetGateway']['InternetGatewayId']
    attach_tag(gateway_id)

    print(">>> ATTACH GATEWAY")
    res = ec2client.attach_internet_gateway(InternetGatewayId=gateway_id,VpcId=vpc_id)
    print("{}".format(res))

def delete_gateway():
    print(">> Detach Gateway")
    res = ec2client.describe_vpcs(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for vpc in res["Vpcs"]:
        res = ec2client.describe_internet_gateways(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
        print("{}".format(res))
        for gateway in res['InternetGateways']:
            res = ec2client.detach_internet_gateway(InternetGatewayId=gateway['InternetGatewayId'],VpcId=vpc['VpcId'])
            print("{}".format(res))

    print(">> Delete Gateway")
    res = ec2client.describe_internet_gateways(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for gateway in res['InternetGateways']:
        res = ec2client.delete_internet_gateway(InternetGatewayId=gateway['InternetGatewayId'])
        print("{}".format(res))

if __name__ == "__main__":
    vpc_id:str = create_vpc()
    gateway_id:str = create_gateway(vpc_id)
    delete_gateway()
    delete_vpc()


```


作成して、削除するだけの、コードができました!!


```
　　　　 ∧＿∧
　／＼（　・∀・）／ヽ
（ ●　と　　　つ　● ）     .. 休憩 ..
　＼/⊂、　 　ノ　＼ノ
　　　　　し’
````


## サブネットを設定
https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html

サブネットを設定しましょう。サブネットは VPCで設定したネットワークを、
さらに分割して、グループ化して管理できます。

```Python:作成
def create_subnet(vpc_id:str):
    print(">>> CREATE SUBNET")
    res = ec2client.create_subnet(CidrBlock='10.1.0.0/24',VpcId=vpc_id)
    print("{}".format(res))
    subnet_id = res['Subnet']['SubnetId']
    attach_tag(subnet_id)
    return subnet_id
```

```Python:削除
def delete_subnet():
    print(">> Delete subnet")
    res = ec2client.describe_subnets(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for subnet in res["Subnets"]:
        res = ec2client.delete_subnet(SubnetId=subnet['SubnetId'])
        print("{}".format(res))
```

CidrBlockは割り振るIPを意味しています。
今回の場合だと
10.1.0.0 から 10.1.0.255 までの IPを、利用できます。

## セキュリテイーグループを設定

どのPortを解放して、どのPortを閉じるかなど、セキュリティーの設定をしてみましょう。

```Python:作成
def create_security_group():
    print(">>> CREATE SECURITY GROUP")
    res = ec2client.create_security_group(Description="AdventCodeServer",GroupName=instance_name)
    print("{}".format(res))
    group_id = res['GroupId']
    attach_tag(group_id)
    return group_id
```

```Python:削除
def delete_security_group():
    res = ec2client.describe_security_groups(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for sg in res['SecurityGroups']:
        res = ec2client.delete_security_group(GroupId=sg["GroupId"])
        print("{}".format(res))
```

```Python:Portの設定を追加
def create_security_group_ingress():
        print(">>>> CREATE SECURITY GROUP INGRESS")
        res = ec2client.authorize_security_group_ingress(
                GroupName=instance_name, IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 8443,
                        'ToPort': 8443,
                        'IpRanges':[
                            {'CidrIp': '0.0.0.0/0', 'Description' : '8443'}
                        ]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 8080,
                        'ToPort': 8080,
                        'IpRanges':[
                            {'CidrIp': '0.0.0.0/0', 'Description' : '8080'}
                        ]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges':[
                            {'CidrIp': '0.0.0.0/0', 'Description' : '8080'}
                        ]
                    },
                ])
        print("{}".format(res))
```


## ここまでを試してみましょう。

```Python
import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
from typing import Dict, List 

instance_name= "advent-code-server"
ec2client:ec2.Client = boto3.client("ec2")



def attach_tag(id:str):
    res = ec2client.create_tags(Resources=[id], Tags=[{"Key": "Name", "Value": instance_name}])
    print("{}".format(res))

def create_vpc():
    print(">>> CREATE VPC")
    res = ec2client.create_vpc(CidrBlock='10.1.0.0/16')
    print("{}".format(res))
    vpc_id = res['Vpc']['VpcId']
    attach_tag(vpc_id)
    return vpc_id

def delete_vpc():
    print(">>> Delete vpcs")
    res = ec2client.describe_vpcs(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for vpc in res["Vpcs"]:
        res = ec2client.delete_vpc(VpcId=vpc['VpcId'])
        print("{}".format(res))
    
def create_gateway(vpc_id:str):
    print(">>> CREATE GATEWAY")
    res = ec2client.create_internet_gateway()
    print("{}".format(res))
    gateway_id = res['InternetGateway']['InternetGatewayId']
    attach_tag(gateway_id)

    print(">>> ATTACH GATEWAY")
    res = ec2client.attach_internet_gateway(InternetGatewayId=gateway_id,VpcId=vpc_id)
    print("{}".format(res))

def delete_gateway():
    print(">> Detach Gateway")
    res = ec2client.describe_vpcs(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for vpc in res["Vpcs"]:
        res = ec2client.describe_internet_gateways(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
        print("{}".format(res))
        for gateway in res['InternetGateways']:
            res = ec2client.detach_internet_gateway(InternetGatewayId=gateway['InternetGatewayId'],VpcId=vpc['VpcId'])
            print("{}".format(res))

    print(">> Delete Gateway")
    res = ec2client.describe_internet_gateways(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for gateway in res['InternetGateways']:
        res = ec2client.delete_internet_gateway(InternetGatewayId=gateway['InternetGatewayId'])
        print("{}".format(res))

def create_subnet(vpc_id:str):
    print(">>> CREATE SUBNET")
    res = ec2client.create_subnet(CidrBlock='10.1.0.0/24',VpcId=vpc_id)
    print("{}".format(res))
    subnet_id = res['Subnet']['SubnetId']
    attach_tag(subnet_id)
    return subnet_id

def delete_subnet():
    print(">> Delete subnet")
    res = ec2client.describe_subnets(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for subnet in res["Subnets"]:
        res = ec2client.delete_subnet(SubnetId=subnet['SubnetId'])
        print("{}".format(res))

def create_security_group():
    print(">>> CREATE SECURITY GROUP")
    res = ec2client.create_security_group(Description="AdventCodeServer",GroupName=instance_name)
    print("{}".format(res))
    group_id = res['GroupId']
    attach_tag(group_id)
    return group_id

def delete_security_group():
    res = ec2client.describe_security_groups(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for sg in res['SecurityGroups']:
        res = ec2client.delete_security_group(GroupId=sg["GroupId"])
        print("{}".format(res))

def create_security_group_ingress():
        print(">>>> CREATE SECURITY GROUP INGRESS")
        res = ec2client.authorize_security_group_ingress(
                GroupName=instance_name, IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 8443,
                        'ToPort': 8443,
                        'IpRanges':[
                            {'CidrIp': '0.0.0.0/0', 'Description' : '8443'}
                        ]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 8080,
                        'ToPort': 8080,
                        'IpRanges':[
                            {'CidrIp': '0.0.0.0/0', 'Description' : '8080'}
                        ]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges':[
                            {'CidrIp': '0.0.0.0/0', 'Description' : '8080'}
                        ]
                    },
                ])
        print("{}".format(res))

if __name__ == "__main__":
    vpc_id:str = create_vpc()
    gateway_id:str = create_gateway(vpc_id)
    subnet_id = create_subnet(vpc_id)
    group_id = create_security_group()
    create_security_group_ingress()
    #create_instance()
    #delete_instance()
    delete_security_group()
    delete_subnet()
    delete_gateway()
    delete_vpc()


```


作成して、削除するだけの、コードができました!!
ネットワークの設定はこれで終わりです。


# 次回

作成した仮想ネットワークに 仮想サーバーを立ち上げてみましょう!!


# コード

https://github.com/kyorohiro/advent-2019-code-server/tree/master/remote_cs01

