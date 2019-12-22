これは、2019年 code-server に Advent Calender の 第14日目の記事です。

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

# はじめに

RouteTable の設定をしていませんでした。 時環境では動いているのですが、
もしかすると動かないかも...

で、Route Table の設定から始めます


# Route Table とは

前回 Gateway を設定しましたね!! で、VPCからアクセスするIPごとに、どのGatewayを使用するかを設定することができます。

今回の場合だと、全部、Internet Gateway につなげれば良いのですが、
VPC間やSubnet間など、こまめに設定することができます。


# ネットワークの作成 その2です

## Route Table を作成する

```python:作成

def create_route_table(vpc_id:str):
    res = ec2client.create_route_table(VpcId=vpc_id)
    print("{}".format(res))
    route_table_id = res['RouteTable']['RouteTableId']
    attach_tag(route_table_id)
    return route_table_id
```

Route Table には VPC をしてします。当然ですね..



とかで行けます

# Routeを作成する

RouteTable に、全てのIPをInternetに接続可能なように指定しましょう

```python:Routeを作成する
def create_route(route_table_id:str, gateway_id:str):
    resp = ec2client.create_route(RouteTableId=route_table_id,DestinationCidrBlock="0.0.0.0/0",GatewayId=gateway_id)
    print("{}".format(resp))
```

`0.0.0.0/0` が全てのIPを意味しています。
 `0.0.0.0` から `255.255.255.255` 

# Subnet に関連付けする


```python:
def associate_route_table(route_table_id:str, subnet_id:str):
    res = ec2client.associate_route_table(RouteTableId=route_table_id,SubnetId=subnet_id)
    print("{}".format(res))
    associate_id = res['AssociationId']
    return associate_id
```

## Route Table を削除

```python
def delete_route_table():
    print(">>> Delete Route Table")
    res = ec2client.describe_route_tables(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for route_table in res["RouteTables"]:
        for association in route_table.get('Associations',[]):
            ec2client.disassociate_route_table(AssociationId = association['RouteTableAssociationId'])
        res = ec2client.delete_route_table(RouteTableId=route_table['RouteTableId'])
        print("{}".format(res))
```


削除はこんな感じです。
削除する前に、`associate_route_table()` を呼び出して、関連付けを外す必要があります。

※ 今回、Tagを利用しているのは、説明しやすいからで、
vpc_id などからも、引っ張ってこれるので、vpc_idを使うのが良いかも

```python
Filters=[{"Name":"vpc-id","Values":[vpc_id]}]
```
## SecurityGroupの修正

前回のコードは、VPCを設定し忘れていました..

```python:作成
def create_security_group(vpc_id):
    print(">>> CREATE SECURITY GROUP")
    res = ec2client.create_security_group(Description="AdventCodeServer",GroupName=instance_name,VpcId=vpc_id)
    print("{}".format(res))
    group_id = res['GroupId']
    attach_tag(group_id)
    return group_id
```

## ここまで書いたコードは以下の通り
https://github.com/kyorohiro/advent-2019-code-server/blob/master/remote_cs01/for_aws/main.py


# Instance を作成する

## PEMファイルを作成する

Instance には、SSH キー を利用して接続をする想定でいます。
秘密鍵と公開鍵を作成しておきましょう

```python:PEM作成
def create_pem():
    pem_file = open("{}.pem".format(instance_name),"w")
    pem_file.write("")
    try:
        print(">>> CREATE KEY_PAIR")
        res = ec2client.create_key_pair(KeyName=instance_name)
        print("{}".format(res))
        pem_file.write(res['KeyMaterial'])
    finally:
        pem_file.close()
    return instance_name
```

```python:PEM削除
def delete_pem():
    print(">>>> DELETE KeyPair")
    ec2client.delete_key_pair(KeyName=instance_name)
```

## Instanceを立ち上げる

```python:作成
def create_instance(subnet_id:str, group_id:str):
    print(">>>> CREATE INSTANCE")
    res = ec2client.run_instances(ImageId="ami-0cd744adeca97abb1",#KeyName="xx",
        InstanceType='t2.micro',
        MinCount=1,MaxCount=1,KeyName=instance_name,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{
                    'Key': 'Name',
                    'Value': instance_name
                }]
            }
        ],NetworkInterfaces=[{"SubnetId":subnet_id,'AssociatePublicIpAddress': True,'DeviceIndex':0,'Groups': [group_id]}]
        )
    print("{}".format(res))
```

作成した subnetと group_id を指定します。

今回はUbuntuを指定しました。
https://aws.amazon.com/jp/amazon-linux-ami/


```python:削除

def delete_instance():
    print(">>>> ec2client.describe_instances")
    res = ec2client.describe_instances(
        Filters=[{"Name":"tag:Name","Values":[instance_name]}]
        )
    print("{}".format(res))

    print(">>>> DELETE Instance")
    for reservation in res['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            res = ec2client.terminate_instances(InstanceIds=[instance_id])

    print("{}".format(res))
```

削除も、今前通りですね。

では、今までに作成したものをつなげてみましょう。

## スクリプトを走らせる、その前に

Instance の削除が完了するまで待機するスクリプトも書いておきましょう。

```python:
def wait_instance_is_terminated():
    while(True):
        res = ec2client.describe_instances(
            Filters=[{"Name":"tag:Name","Values":[instance_name]}]
            )
        terminated = False
        for reservation in res['Reservations']:
            for instance in reservation['Instances']:
                instance_state = instance['State']['Name']
                print("------{}".format(instance_state))
                if instance_state != 'terminated':
                    terminated = True
        if terminated == False:
            break
        time.sleep(6)

```

## まとめ


```python:main.py
import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
from typing import Dict, List 
import time
import network

instance_name= "advent-code-server"
ec2client:ec2.Client = boto3.client("ec2")


def create_pem():
    pem_file = open("{}.pem".format(instance_name),"w")
    pem_file.write("")
    try:
        print(">>> CREATE KEY_PAIR")
        res = ec2client.create_key_pair(KeyName=instance_name)
        print("{}".format(res))
        pem_file.write(res['KeyMaterial'])
    finally:
        pem_file.close()
    return instance_name

def delete_pem():
    print(">>>> DELETE KeyPair")
    ec2client.delete_key_pair(KeyName=instance_name)

def create_instance(subnet_id:str, group_id:str):

    print(">>>> CREATE INSTANCE")
    # Ubuntu Server 18.04 LTS (HVM), SSD Volume Type - ami-0cd744adeca97abb1 (64-bit x86) / ami-0f0dcd3794e1da1e1 (64-bit Arm)
    # https://aws.amazon.com/jp/amazon-linux-ami/
    res = ec2client.run_instances(ImageId="ami-0cd744adeca97abb1",#KeyName="xx",
        InstanceType='t2.micro',
        MinCount=1,MaxCount=1,KeyName=instance_name,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                {
                    'Key': 'Name',
                    'Value': instance_name
                }
                ]
            }
        ],NetworkInterfaces=[{"SubnetId":subnet_id,'AssociatePublicIpAddress': True,'DeviceIndex':0,'Groups': [group_id]}]
        )
    print("{}".format(res))

    return instance_name


def delete_instance():
    print(">>>> ec2client.describe_instances")
    res = ec2client.describe_instances(
        Filters=[{"Name":"tag:Name","Values":[instance_name]}]
        )
    print("{}".format(res))

    print(">>>> DELETE Instance")
    for reservation in res['Reservations']:
        for instance in reservation['Instances']:
            print("------{}".format(instance))
            instance_id = instance['InstanceId']
            print(">>>> {}".format(instance_id))
            res = ec2client.terminate_instances(InstanceIds=[instance_id])

    print("{}".format(res))

def wait_instance_is_terminated():
    while(True):
        res = ec2client.describe_instances(
            Filters=[{"Name":"tag:Name","Values":[instance_name]}]
            )
        terminated = False
        for reservation in res['Reservations']:
            for instance in reservation['Instances']:
                instance_state = instance['State']['Name']
                print("------{}".format(instance_state))
                if instance_state != 'terminated':
                    terminated = True
        if terminated == False:
            break
        time.sleep(6)

if __name__ == "__main__":
    res = network.create()
    create_pem()
    create_instance(res["subnet_id"], res["group_id"])
    delete_instance()
    wait_instance_is_terminated()
    delete_pem()
    network.delete()

```

コード全体は、以下

https://github.com/kyorohiro/advent-2019-code-server/tree/master/remote_cs02/for_aws




# 次回

作成した仮想 Instance を操作してみましょう!!


# コード

https://github.com/kyorohiro/advent-2019-code-server/tree/master/remote_cs02



