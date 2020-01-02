import boto3
import sys, getopt
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
from typing import Dict, List 
import time
from aws.network import AWSNetwork
from aws.instance import AWSInstance


def create_network(network:AWSNetwork):
    print(">>> Create")
    vpc_id:str = network.create_vpc()
    gateway_id:str = network.create_gateway(vpc_id)
    subnet_id = network.create_subnet(vpc_id)
    group_id = network.create_security_group(vpc_id)
    network.create_security_group_ingress(group_id)
    route_table_id = network.create_route_table(vpc_id)
    network.create_route(route_table_id, gateway_id)
    network.associate_route_table(route_table_id, subnet_id)
    return  {
        "vpc_id":vpc_id,
        "gateway_id":gateway_id,
        "subnet_id":subnet_id,
        "group_id":group_id,
        "route_table_id":route_table_id
    }


def delete_network(network:AWSNetwork):
    print(">>> Delete")
    res = network.list_vpc()
    print("{}".format(res))

    # delete at vpc_id
    for vpc in res["Vpcs"]:
        vpc_id=vpc['VpcId']
        network.delete_route_table(vpc_id)
        network.delete_security_group(vpc_id)
        network.delete_subnet(vpc_id) 
        network.delete_gateway(vpc_id)
        #delete_vpc(vpc_id)

    # delete at instance name
    network.delete_route_table()
    network.delete_security_group()
    network.delete_subnet()
    network.delete_gateway()
    network.delete_vpc()

def create_intance(instance:AWSInstance, network:AWSNetwork):
    instance.create_pem()
    instance.create_instance(subnet_id=network.subnet_id, group_id=network.group_id)

def delete_intance(instance:AWSInstance):
    instance.delete_pem()
    instance.delete_instance()

def get_inst(ec2_client:ec2.Client, project_name="advent-code-server"):
    try:
        print(">>>> ec2client.describe_instances")
        res = ec2_client.describe_instances(Filters=[{"Name":"tag:Name","Values":[project_name]}])
        print("{}".format(res))

        for reserve_info in res['Reservations']:
            print("-")
            for instance_info in reserve_info['Instances']:
                print(">>>> {}".format(instance_info.get('InstanceId',"")))
                print(">>>> {}".format(instance_info.get('PublicDnsName',"")))
                print(">>>> {}".format(instance_info.get('PublicIpAddress',"")))
                print(">>>> {}".format(instance_info.get('PrivateDnsName',"")))
                print(">>>> {}".format(instance_info.get('PrivateIpAddress',"")))
                print(">>>> {}".format(instance_info.get('State',"")))
 
    except ClientError as e:
        print("-- {}".format(e.response))

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], ":hcdg", ["help", "create","delete","get"])
    except getopt.GetoptError as err:
        raise err

    opts = [("-h")] if len(opts) == 0 else opts
    project_name = "advent-instance"
    ec2_client:ec2.Client = boto3.client("ec2")
    network:AWSNetwork = AWSNetwork(ec2_client, project_name=project_name, ports=[22,8443,8080], vpc_cidr_block='10.1.0.0/16', subnet_cidr_block='10.1.0.0/24')
    instance:AWSInstance = AWSInstance(ec2_client, project_name=project_name, instance_type='t2.micro', image_id="ami-0cd744adeca97abb1")

    for o, a in opts:
        if o in ("-c", "--create"):
            print(">CREATE")
            network.create_network()
            create_intance(instance, network)
            file = open(f'{project_name}.pem', "w")
            file.write(instance.pem_data)
            file.close()
        elif o in ("-d", "--delete"):
            print(">DELETE")
            delete_intance(instance)
            instance.wait_instance_is_terminated()
            delete_network(network)
        elif o in ("-g","--get"):
            get_inst(ec2_client, project_name)
        else:
            print(f"[how to use]")
            print(f"python main.py --create ")
            print(f"python main.py --delete ")




