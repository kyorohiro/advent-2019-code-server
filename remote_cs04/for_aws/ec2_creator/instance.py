
import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
import json
import time
from typing import Dict, List 


class Instance:

    def __init__(self):
        self._name = "advent-instance"
        self._ec2client:ec2.Client = boto3.client("ec2")
        self._instance_type = 't2.micro'
        self._image_type = "ami-0cd744adeca97abb1"
        self._instance_id = None
        self._pem = None
 

    def create_key_pair(self) -> str:
        print(">>> CREATE KEY_PAIR")
        res = self._ec2client.create_key_pair(KeyName=self._name)
        print("{}".format(res))
        self._pem = res['KeyMaterial']
        return self._pem
 
    def delete_key_pair(self):
        print(">>>> DELETE KeyPair")
        self._ec2client.delete_key_pair(KeyName=self._name)

    def to_dict(self) -> Dict[str,str]:
        return {
            "name" : self._name,
            "instance_type" : self._instance_type,
            "image_type" : self._image_type,
            "instance_id" : self._instance_id,
            "pem" : self._pem
        }

    def create_ec2_instance(self):
        print(">>>> CREATE INSTANCE")
        # Ubuntu Server 18.04 LTS (HVM), SSD Volume Type - ami-0cd744adeca97abb1 (64-bit x86) / ami-0f0dcd3794e1da1e1 (64-bit Arm)
        # Ubuntu Server 18.04 LTS (HVM), SSD Volume Type - ami-0cd744adeca97abb1 (64-bit x86) / ami-0f0dcd3794e1da1e1 (64-bit Arm)
        # https://aws.amazon.com/jp/amazon-linux-ami/
        res = self._ec2client.run_instances(ImageId=self._image_type,
            SecurityGroups=[self._name], InstanceType=self._instance_type,
            MinCount=1,MaxCount=1,KeyName=self._name ,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                    {
                        'Key': 'Name',
                        'Value': self._name
                    }
                    ]
                }
            ]
            )
        print("{}".format(res))
        self._instance_id = res['Instances'][0]['InstanceId']

    def delete_ec2_instance(self):
        print(">>>> DELETE Instance")
        res = self._ec2client.describe_instances(
            Filters=[{"Name":"tag:Name","Values":[self._name]}]
            )
        print("{}".format(res))

        for reservation in res['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                res = self._ec2client.terminate_instances(InstanceIds=[instance_id])

        print("{}".format(res))
        
    def create_instance(self):
        '''
        
        '''
        pem_file = open("{}.pem".format(self._name),"w")
        info_file = open("instance_info_{}_{}.json".format(self._name, time.time()),"w")
        pem_file.write("")
        info_file.write("")
        try:
            self.create_key_pair()
            self.create_ec2_instance()
        finally:
            pem_file.write(self._pem)
            info:Dict = self.to_dict()
            info["pem"] = ""
            info_file.write(json.dumps(info))
            pem_file.close()
            info_file.close()
        
    def wait_instance_is_terminated(self):
        while(True):
            res = self._ec2client.describe_instances(
                Filters=[{"Name":"tag:Name","Values":[self._name]}]
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

