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

'''
{
    "vpc_id":vpc_id,
    "gateway_id":gateway_id,
    "subnet_id":subnet_id,
    "group_id":group_id,
    "route_table_id":route_table_id
}
'''

