import boto3
import sys, getopt
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
from typing import Dict, List 
import time
from aws.network import AWSNetwork
from aws.instance import AWSInstance
from aws.template import create_network, delete_network, create_instance, delete_instance, get_inst

## PARAMS
project_name = "advent-instance"
ports = [22,8443,8080]
vpc_cidr_block = '10.1.0.0/16'
subnet_cidr_block = '10.1.0.0/24'
instance_type = 't2.micro'
image_id = "ami-0cd744adeca97abb1"


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], ":hcdg", ["help", "create","delete","get"])
    except getopt.GetoptError as err:
        raise err

    opts = [("-h")] if len(opts) == 0 else opts
    project_name = "advent-instance"
    ec2_client:ec2.Client = boto3.client("ec2")
    network:AWSNetwork = AWSNetwork(ec2_client, project_name=project_name, ports=ports, vpc_cidr_block=vpc_cidr_block, subnet_cidr_block=subnet_cidr_block)
    instance:AWSInstance = AWSInstance(ec2_client, project_name=project_name, instance_type=instance_type, image_id=image_id)

    for o, a in opts:
        if o in ("-c", "--create"):
            print(">CREATE")
            create_network(network)
            create_instance(instance, network)
            file = open(f'{project_name}.pem', "w")
            file.write(instance.pem_data)
            file.close()
        elif o in ("-d", "--delete"):
            print(">DELETE")
            delete_instance(instance)
            instance.wait_instance_is_terminated()
            delete_network(network)
        elif o in ("-g","--get"):
            print(get_inst(ec2_client, project_name))
        else:
            print(f"[how to use]")
            print(f"python main.py --create ")
            print(f"python main.py --delete ")




