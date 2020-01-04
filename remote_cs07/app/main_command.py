import boto3
import sys, getopt
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
from typing import Dict, List 
import time
from aws.network import AWSNetwork
from aws.instance import AWSInstance
from aws.template import create_network, delete_network, create_instance, delete_instance, get_inst, get_ip
import paramiko
import re
## PARAMS
project_name = "advent-instance"
ports = [22,8443,8080]
vpc_cidr_block = '10.1.0.0/16'
subnet_cidr_block = '10.1.0.0/24'
instance_type = 't2.micro'
image_id = "ami-0cd744adeca97abb1"
git = "https://github.com/kyorohiro/advent-2019-code-server.git"
git_dir = "advent-2019-code-server"
path = "remote_cs07"
sh = "sh create.sh"
password = "password1224"


def run_command(client: paramiko.SSHClient, command: str):
    print(f"run>{command}\n")
    stdin, stdout, stderr = client.exec_command(command)
    d = stdout.read().decode('utf-8')
    print(f"stdout>\n{d}")
    d = stderr.read().decode('utf-8')
    print(f"stderr>\n{d}")
    return stdin

def run_script(ip:str, rsa_key_path:str):
    rsa_key: paramiko.rsakey.RSAKey = paramiko.rsakey.RSAKey.from_private_key_file(rsa_key_path)
    client: paramiko.SSHClient = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username="ubuntu", pkey=rsa_key)

    run_command(client, "sudo apt-get update")
    run_command(client, "sudo apt-get install -y docker.io")
    run_command(client, "sudo apt-get install -y git")
    run_command(client, "sudo apt-get install docker-compose -y")
    run_command(client, f"mkdir {project_name}")
    run_command(client, f"cd {project_name} ; git clone {git}")
    run_command(client, f"cd {project_name}/{git_dir}/{path} ; sudo {sh} {password}")


    #run_command(client, "sudo docker run -p 0.0.0.0:8080:8080 -p0.0.0.0:8443:8443 codercom/code-server:v2 --cert")
    
    client.close()


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], ":hcdgs", ["help", "create","delete","get","start"])
    except getopt.GetoptError as err:
        raise err

    opts = [("-h")] if len(opts) == 0 else opts
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
            file.flush()
            file.close()
            instance.wait_instance_is_running()
            # following sleep is for ports 22 
            time.sleep(10)
            ip_list = get_ip(ec2_client, project_name)
            if len(ip_list) > 0:
                run_script(ip_list[0],f"{project_name}.pem")
        elif o in ("-d", "--delete"):
            print(">DELETE")
            delete_instance(instance)
            instance.wait_instance_is_terminated()
            delete_network(network)
        elif o in ("-g","--get"):
            print(get_inst(ec2_client, project_name))
        elif o in ("-s","--start"):
            ip_list = get_ip(ec2_client, project_name)
            if len(ip_list) > 0:
                run_script(ip_list[0],f"{project_name}.pem")
        else:
            print(f"[how to use]")
            print(f"python main.py --create ")
            print(f"python main.py --delete ")




