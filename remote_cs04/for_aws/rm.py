import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
import time

instance_name= "advent-code-server"
ec2client:ec2.Client = boto3.client("ec2")


def rm_instance():
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

def rm_network():
    print(">> Delete security group {}".format(instance_name))
    res = ec2client.describe_security_groups(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for sg in res['SecurityGroups']:
        res = ec2client.delete_security_group(GroupId=sg["GroupId"])
        print("{}".format(res))

    print(">> Delete subnet")
    res = ec2client.describe_subnets(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for subnet in res["Subnets"]:
        res = ec2client.delete_subnet(SubnetId=subnet['SubnetId'])
        print("{}".format(res))

    print(">> Delete route_table")
    res = ec2client.describe_route_tables(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for route_table in res['RouteTables']:
        res = ec2client.delete_route_table(RouteTableId=route_table['RouteTableId'])
        print("{}".format(res))

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

    print(">>> Delete vpcs")
    res = ec2client.describe_vpcs(Filters=[{"Name":"tag:Name","Values":[instance_name]}])
    print("{}".format(res))
    for vpc in res["Vpcs"]:
        res = ec2client.delete_vpc(VpcId=vpc['VpcId'])
        print("{}".format(res))
    

if __name__ == "__main__":
    rm_instance()
    wait_instance_is_terminated()
    rm_network()
