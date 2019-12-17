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

