import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
from typing import Dict, List 
import time
instance_name= "advent-code-server"
ec2client:ec2.Client = boto3.client("ec2")



def attach_tag(id:str):
    print(">>> ATACH TAG {}".format(id))
    res = ec2client.create_tags(Resources=[id], Tags=[{"Key": "Name", "Value": instance_name}])
    print("{}".format(res))

def create_vpc():
    print(">>> CREATE VPC")
    res = ec2client.create_vpc(CidrBlock='10.1.0.0/16')
    print("{}".format(res))
    vpc_id = res['Vpc']['VpcId']
    attach_tag(vpc_id)
    return vpc_id

def delete_vpc(vpc_id=None):
    print(">>> Delete vpcs")
    if vpc_id is None:
        res = ec2client.describe_vpcs(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    else:
        res = ec2client.describe_vpcs(Filters=[{"Name":"vpc-id","Values":[vpc_id]}])

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

def delete_route_table(vpc_id=None):
    print(">>> Delete Route Table")
    if vpc_id == None:
        res = ec2client.describe_route_tables(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    else:
        res = ec2client.describe_route_tables(Filters=[{"Name":"vpc-id","Values":[vpc_id]}])

    print("{}".format(res))
    for route_table in res["RouteTables"]:
        associations = route_table.get('Associations',[])
        associations_with_main = [a for a in associations if a.get('Main',False)]
        if len(associations_with_main) > 0:
            continue
        for association in associations:
            if association.get('Main',False):
                # infnore main table
                continue
            ec2client.disassociate_route_table(AssociationId = association['RouteTableAssociationId'])
        res = ec2client.delete_route_table(RouteTableId=route_table['RouteTableId'])
        print("{}".format(res))

def create_route(route_table_id:str, gateway_id:str):
    resp = ec2client.create_route(RouteTableId=route_table_id,DestinationCidrBlock="0.0.0.0/0",GatewayId=gateway_id)
    print("{}".format(resp))

def delete_route(vpc_id=None):
    if vpc_id == None:
        res = ec2client.describe_route_tables(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    else:
         res = ec2client.describe_route_tables(Filters=[{"Name":"vpc-id","Values":[vpc_id]}])     
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

def delete_gateway(vpc_id=None):
    print(">> Detach Gateway")
    if vpc_id is not None:
        if vpc_id is None:
            res = ec2client.describe_internet_gateways(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
        else:
            res = ec2client.describe_internet_gateways(Filters=[{"Name":"attachment.vpc-id","Values":[vpc_id]}])
        print("{}".format(res))
        for  gateway in res['InternetGateways']:
            res = ec2client.detach_internet_gateway(InternetGatewayId=gateway['InternetGatewayId'],VpcId=vpc_id)
            print("{}".format(res))

    if vpc_id is None:
        res = ec2client.describe_internet_gateways(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    else:
        res = ec2client.describe_internet_gateways(Filters=[{"Name":"attachment.vpc-id","Values":[vpc_id]}])
    print(">> Delete Gateway")
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

def delete_subnet(vpc_id=None):
    print(">> Delete subnet")
    if vpc_id is None:
        res = ec2client.describe_subnets(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    else:
        res = ec2client.describe_subnets(Filters=[{"Name":"vpc-id","Values":[vpc_id]}])

    print("{}".format(res))
    for subnet in res["Subnets"]:
        res = ec2client.delete_subnet(SubnetId=subnet['SubnetId'])
        print("{}".format(res))

def create_security_group(vpc_id):
    print(">>> CREATE SECURITY GROUP")
    res = ec2client.create_security_group(Description="AdventCodeServer",GroupName=instance_name,VpcId=vpc_id)
    print("{}".format(res))
    group_id = res['GroupId']
    attach_tag(group_id)
    return group_id

def delete_security_group(vpc_id=None):
    if vpc_id is None:
        res = ec2client.describe_security_groups(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    else:
        res = ec2client.describe_security_groups(Filters=[{"Name":"vpc-id","Values":[vpc_id]}])
    print("{}".format(res))
    for sg in res['SecurityGroups']:
        if sg.get('GroupName','default') == 'default':
            # ignore defalut 
            continue
        res = ec2client.delete_security_group(GroupId=sg["GroupId"])
        print("{}".format(res))

def create_security_group_ingress(group_id):
        print(">>>> CREATE SECURITY GROUP INGRESS")
        res = ec2client.authorize_security_group_ingress(
                GroupId=group_id, IpPermissions=[
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


def create():
    vpc_id:str = create_vpc()
    gateway_id:str = create_gateway(vpc_id)
    subnet_id = create_subnet(vpc_id)
    group_id = create_security_group(vpc_id)
    create_security_group_ingress(group_id)
    route_table_id = create_route_table(vpc_id)
    create_route(route_table_id, gateway_id)
    associate_route_table(route_table_id, subnet_id)

def delete():
    print(">>> Delete vpcs")
    res = ec2client.describe_vpcs(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    # delete at vpc_id
    for vpc in res["Vpcs"]:
        vpc_id=vpc['VpcId']
        delete_route_table(vpc_id)
        delete_security_group(vpc_id)
        delete_subnet(vpc_id) 
        delete_gateway(vpc_id)
        #delete_vpc(vpc_id)

    # delete at instance name
    delete_route_table()
    delete_security_group()
    delete_subnet()
    delete_gateway()
    delete_vpc()

if __name__ == "__main__":
    create()
    delete()
