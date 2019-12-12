import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError

security_group = "advent-code-server-security-group"
ec2_instance_key_name= "advent-code-server"
ec2client:ec2.Client = boto3.client("ec2")

def end():
    try:
        print(">>>> ec2client.delete_key_pair")
        ec2client.delete_key_pair(KeyName=ec2_instance_key_name)
    except ClientError as e:
        print("-- {}".format(e.response))
    
    try:
        print(">>>> ec2client.describe_instances")
        res = ec2client.describe_instances(
            Filters=[{"Name":"tag:Name","Values":[ec2_instance_key_name]}]
            )
        print("{}".format(res))
        instance_id = res['Reservations'][0]['Instances'][0]['InstanceId']

        print(">>>> ec2client.terminate_instances")
        res = ec2client.terminate_instances(InstanceIds=[instance_id])
        print("{}".format(res))

    except ClientError as e:
        print("-- {}".format(e.response))
    
    try:
        print(">>>> ec2client.delete_security_group")
        res = ec2client.delete_security_group(GroupName=security_group)
        print("{}".format(res))
    except ClientError as e:
        print("-- {}".format(e.response))
    #ec2client.terminate_instances()


if __name__ == "__main__":
    end()
