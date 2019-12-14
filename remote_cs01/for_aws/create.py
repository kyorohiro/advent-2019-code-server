import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
import json
import time
from typing import Dict, List 

instance_name= "advent-code-server"

ec2client:ec2.Client = boto3.client("ec2")


# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.Client.create_vpc
def create_network():
    file = open("network_info_{}_{}.json".format(instance_name, time.time()),"w")
    file.write("")
    network_info = {}
    try:
        print(">>> CREATE VPC")
        res = ec2client.create_vpc(CidrBlock='10.1.0.0/16')
        print("{}".format(res))
        vpc_id = res['Vpc']['VpcId']
        network_info["vpc_info"] = vpc_id
        res = ec2client.create_tags(Resources=[vpc_id], Tags=[{"Key": "Name", "Value": instance_name}])
        print("{}".format(res))


        print(">>> CREATE GATEWAY")
        res = ec2client.create_internet_gateway()
        print("{}".format(res))
        gateway_id = res['InternetGateway']['InternetGatewayId']
        network_info["gateway_id"] = gateway_id
        res = ec2client.create_tags(Resources=[gateway_id], Tags=[{"Key": "Name", "Value": instance_name}])
        print("{}".format(res))

        res = ec2client.attach_internet_gateway(InternetGatewayId=gateway_id,VpcId=vpc_id)
        print("{}".format(res))
        
        print(">>> CREATE ROUTE TABLE")
        res = ec2client.create_route_table(VpcId=vpc_id)
        print("{}".format(res))
        route_table_id = res['RouteTable']['RouteTableId']
        network_info["route_table_id"] = route_table_id
        res = ec2client.create_tags(Resources=[route_table_id], Tags=[{"Key": "Name", "Value": instance_name}])
        print("{}".format(res))

        print(">>> CREATE SUBNET")
        res = ec2client.create_subnet(CidrBlock='10.1.0.0/24',VpcId=vpc_id)
        subnet_id = res['Subnet']['SubnetId']
        network_info["subnet_id"] = subnet_id 
        res = ec2client.create_tags(Resources=[subnet_id], Tags=[{"Key": "Name", "Value": instance_name}])
        print("{}".format(res))

        print(">>> CREATE SECURITY GROUP")
        res = ec2client.create_security_group(Description="AdventCodeServer",GroupName=instance_name)
        print("{}".format(res))
        group_id = res['GroupId']
        network_info["group_id"] = group_id
        res = ec2client.create_tags(Resources=[group_id], Tags=[{"Key": "Name", "Value": instance_name}])
        print("{}".format(res))
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
    finally:
        file.write(json.dumps(network_info))
        file.close()

    return network_info

def create_instance(network_info:Dict):

    pem_file = open("{}.pem".format(instance_name),"w")
    info_file = open("instance_info_{}_{}.json".format(instance_name, time.time()),"w")
    pem_file.write("")
    info_file.write("")
    instance_info = {}
    try:
        print(">>> CREATE KEY_PAIR")
        res = ec2client.create_key_pair(KeyName=instance_name)
        print("{}".format(res))
        pem_file.write(res['KeyMaterial'])
        print(">>>> CREATE INSTANCE")
        instance_info["key_name"] = instance_name
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
        instance_info["instance_id"] = res['Instances'][0]['InstanceId']
    finally:
        info_file.write(json.dumps(instance_info))
        pem_file.close()
        info_file.close()
    return instance_name


if __name__ == "__main__":
    network_info = create_network()
    instance_info = create_instance(network_info)

