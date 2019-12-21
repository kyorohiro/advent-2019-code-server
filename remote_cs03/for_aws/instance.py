import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
from typing import Dict, List 
import time
import network

ec2client:ec2.Client = boto3.client("ec2")

class CodeServerInsrance:

    def __init__(self, ec2_client: ec2.Client, project_name="advent-code-server", instance_type='t2.micro', image_id="ami-0cd744adeca97abb1"):
        self._ec2_client:ec2.Client = ec2_client
        self._project_name:str = project_name
        self._instance_type = instance_type
        self._pem_data:str = ""
        self._image_id=image_id

    @property
    def ec2_client(self):
        return self._ec2_client

    @property
    def project_name(self):
        return self._project_name

    @property
    def instance_type(self):
        return self._instance_type

    @property
    def pem_data(self):
        return self._pem_data

    @property
    def image_id(self):
        return self._image_id

    def create_pem(self):
        print(">>> CREATE KEY_PAIR")
        res = ec2client.create_key_pair(KeyName=self._project_name)
        print("{}".format(res))
        self._pem_data =res['KeyMaterial']

    def delete_pem(self):
        print(">>>> DELETE KeyPair")
        ec2client.delete_key_pair(KeyName=self._project_name)

    def create_instance(self, subnet_id:str, group_id:str):
        print(">>>> CREATE INSTANCE")
        res = ec2client.run_instances(ImageId=self._image_id,
            InstanceType=self._instance_type,
            MinCount=1,MaxCount=1,KeyName=self._project_name,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{
                    'Key': 'Name',
                    'Value': self._project_name
                }]
            }],
            NetworkInterfaces=[{"SubnetId":subnet_id, 'AssociatePublicIpAddress': True, 'DeviceIndex':0,'Groups': [group_id]}]
            )
        print("{}".format(res))

        return self._project_name


    def delete_instance(self):
        print(">>>> ec2client.describe_instances")
        res = ec2client.describe_instances(
            Filters=[{"Name":"tag:Name","Values":[self._project_name]}]
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

    def wait_instance_is_terminated(self):
        while(True):
            res = ec2client.describe_instances(
                Filters=[{"Name":"tag:Name","Values":[self._project_name]}]
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


'''
{
    "vpc_id":vpc_id,
    "gateway_id":gateway_id,
    "subnet_id":subnet_id,
    "group_id":group_id,
    "route_table_id":route_table_id
}
'''

