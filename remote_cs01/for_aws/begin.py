import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError

security_group = "advent-code-server-security-group"
ec2_instance_key_name= "advent-code-server"
ec2client:ec2.Client = boto3.client("ec2")

def begin():
    print(">>>> ec2client.create_security_group ")
    try:
        res = ec2client.create_security_group(Description="AdventCodeServer",GroupName=security_group)
        print("{}".format(res))
    except ClientError as e:
        print("-- {}".format(e.response))
        if e.response["Error"]["Code"] != 'InvalidGroup.Duplicate':
            exit

    print(">>>> ec2client.authorize_security_group_ingress ")
    try:
        res = ec2client.authorize_security_group_ingress(
                GroupName=security_group, IpPermissions=[
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
    except ClientError as e:
        print("-- {}".format(e.response))
        if e.response["Error"]["Code"] != 'InvalidPermission.Duplicate':
            exit

    print(">>>> ec2client.create_key_pair")
    try:
        res = ec2client.create_key_pair(KeyName=ec2_instance_key_name)
        print("{}".format(res))
        file = open("{}.pem".format(ec2_instance_key_name),"w")
        file.write(res['KeyMaterial'])
        file.close()
        
        #instance_id = res['Instances'][0]['InstanceId']
    except ClientError as e:
        print("-- {}".format(e.response))

    print(">>>> ec2client.run_instances ")
    try:
        # Ubuntu Server 18.04 LTS (HVM), SSD Volume Type - ami-0cd744adeca97abb1 (64-bit x86) / ami-0f0dcd3794e1da1e1 (64-bit Arm)
        # Ubuntu Server 18.04 LTS (HVM), SSD Volume Type - ami-0cd744adeca97abb1 (64-bit x86) / ami-0f0dcd3794e1da1e1 (64-bit Arm)
        # https://aws.amazon.com/jp/amazon-linux-ami/
        res = ec2client.run_instances(ImageId="ami-0cd744adeca97abb1",#KeyName="xx",
            SecurityGroups=[security_group], InstanceType='t2.micro',
            MinCount=1,MaxCount=1,KeyName=ec2_instance_key_name,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                    {
                        'Key': 'Name',
                        'Value': ec2_instance_key_name
                    }
                    ]
                }
            ]
            )
        print("{}".format(res))
        #instance_id = res['Instances'][0]['InstanceId']
    except ClientError as e:
        print("-- {}".format(e.response))


if __name__ == "__main__":
    begin()

