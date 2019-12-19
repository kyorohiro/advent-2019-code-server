import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
from typing import Dict, List 
import time
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

def create_route_table(vpc_id:str):
    res = ec2client.create_route_table(VpcId=vpc_id)
    print("{}".format(res))
    route_table_id = res['RouteTable']['RouteTableId']
    attach_tag(route_table_id)
    return route_table_id

def delete_route_table():
    print(">>> Delete Route Table")
    res = ec2client.describe_route_tables(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for route_table in res["RouteTables"]:
        for association in route_table.get('Associations',[]):
            ec2client.disassociate_route_table(AssociationId = association['RouteTableAssociationId'])
        res = ec2client.delete_route_table(RouteTableId=route_table['RouteTableId'])
        print("{}".format(res))

def create_route(route_table_id:str, gateway_id:str):
    resp = ec2client.create_route(RouteTableId=route_table_id,DestinationCidrBlock="0.0.0.0/0",GatewayId=gateway_id)
    print("{}".format(resp))

def delete_route():
    res = ec2client.describe_route_tables(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for route_table in res["RouteTables"]:
        resp = ec2client.delete_route(DestinationCidrBlock="0.0.0.0/0",RouteTableId=route_table['RouteTableId'])
        print("{}".format(resp))

def associate_route_table(route_table_id:str, subnet_id:str):
    res = ec2client.associate_route_table(RouteTableId=route_table_id,SubnetId=subnet_id)
    print("{}".format(res))
    associate_id = res['AssociationId']
    return associate_id


def create_gateway(vpc_id:str):
    print(">>> CREATE GATEWAY")
    res = ec2client.create_internet_gateway()
    print("{}".format(res))
    gateway_id = res['InternetGateway']['InternetGatewayId']
    attach_tag(gateway_id)

    print(">>> ATTACH GATEWAY")
    res = ec2client.attach_internet_gateway(InternetGatewayId=gateway_id,VpcId=vpc_id)
    print("{}".format(res))
    return gateway_id

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


def create_instance():

    pem_file = open("{}.pem".format(instance_name),"w")
    pem_file.write("")
    try:
        print(">>> CREATE KEY_PAIR")
        res = ec2client.create_key_pair(KeyName=instance_name)
        print("{}".format(res))
        pem_file.write(res['KeyMaterial'])
        print(">>>> CREATE INSTANCE")
        # Ubuntu Server 18.04 LTS (HVM), SSD Volume Type - ami-0cd744adeca97abb1 (64-bit x86) / ami-0f0dcd3794e1da1e1 (64-bit Arm)
        # Ubuntu Server 18.04 LTS (HVM), SSD Volume Type - ami-0cd744adeca97abb1 (64-bit x86) / ami-0f0dcd3794e1da1e1 (64-bit Arm)
        # https://aws.amazon.com/jp/amazon-linux-ami/
        res = ec2client.run_instances(ImageId="ami-0cd744adeca97abb1",#KeyName="xx",
            SecurityGroups=[instance_name], InstanceType='t2.micro',
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
            ]
            )
        print("{}".format(res))
    finally:
        pem_file.close()
    return instance_name


def delete_instance():
    print(">>>> DELETE KeyPair")
    ec2client.delete_key_pair(KeyName=instance_name)
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
    vpc_id:str = create_vpc()
    gateway_id:str = create_gateway(vpc_id)
    subnet_id = create_subnet(vpc_id)
    group_id = create_security_group()
    create_security_group_ingress()
    route_table_id = create_route_table(vpc_id)
    create_route(route_table_id, gateway_id)
    associate_route_table(route_table_id, subnet_id)    
    create_instance()
    delete_instance()
    wait_instance_is_terminated()
    delete_route_table()    
    delete_security_group()
    delete_subnet()
    delete_gateway()
    delete_vpc()

    res = ec2client.describe_route_tables(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))

    print(">>> Delete vpcs")
    res = ec2client.describe_vpcs(Filters=[{"Name":"tag:Name","Values":[instance_name]}])

    ec2client.describe_subnets()
    print("{}".format(res))