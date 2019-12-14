import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError

instance_name= "advent-code-server"
ec2client:ec2.Client = boto3.client("ec2")


def get_inst():

    try:
        print(">>>> ec2client.describe_instances")
        res = ec2client.describe_instances(
            Filters=[{"Name":"tag:Name","Values":[instance_name]}]
            )
        print("{}".format(res))

        print("----")
        print("----")
        for reserve_info in res['Reservations']:
            print("-")
            for instance_info in reserve_info['Instances']:
                print(">>>> {}".format(instance_info.get('InstanceId',"")))
                print(">>>> {}".format(instance_info.get('PublicDnsName',"")))
                print(">>>> {}".format(instance_info.get('PublicIpAddress',"")))
                print(">>>> {}".format(instance_info.get('PrivateDnsName',"")))
                print(">>>> {}".format(instance_info.get('PrivateIpAddress',"")))
                print(">>>> {}".format(instance_info.get('State',"")))

        print("----")
        print("----")
 
    except ClientError as e:
        print("-- {}".format(e.response))
 
if __name__ == "__main__":
    get_inst()

