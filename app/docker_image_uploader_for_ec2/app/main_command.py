import boto3
import sys, getopt
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
from typing import Dict, List 
import time
from aws.network import AWSNetwork
from aws.instance import AWSInstance
from aws.template import create_network, delete_network, create_instance, delete_instance, get_inst, get_ip, stop_running_instance, start_stopped_instance
import paramiko
import re
import logging
logging.basicConfig(level=logging.INFO)

## PARAMS
project_name = "advent-instance"
ports = [22,8443,8080]
vpc_cidr_block = '10.1.0.0/16'
subnet_cidr_block = '10.1.0.0/24'
instance_type = 't2.micro'
image_id = "ami-0cd744adeca97abb1"
git = "https://github.com/kyorohiro/advent-2019-code-server.git"
git_dir = "advent-2019-code-server"
path = "app/docker_image_uploader_for_ec2"
sh = "sh create.sh"
password = "password1224"


def run_command_on_instance(client: paramiko.SSHClient, command: str):
    logging.info(f"# run>{command}\n")
    stdin, stdout, stderr = client.exec_command(command)
    d = stdout.read().decode('utf-8')
    logging.info(f"# stdout>\n{d}")
    d = stderr.read().decode('utf-8')
    logging.info(f"# stderr>\n{d}")
    return stdin

def create_app(ip:str, rsa_key_path:str):
    logging.info(f"# run_create_script {ip}\n")
    rsa_key: paramiko.rsakey.RSAKey = paramiko.rsakey.RSAKey.from_private_key_file(rsa_key_path)
    client: paramiko.SSHClient = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for i in range(3):
        try:
            client.connect(ip, username="ubuntu", pkey=rsa_key)
            break
        except:
            pass
        time.sleep(6)
        logging.info(f"RETRY CONNECT {i+1}")

    logging.info(f"# run_create_script connected \n")
    run_command_on_instance(client, "sudo apt-get update")
    run_command_on_instance(client, "sudo apt-get install -y docker.io")
    run_command_on_instance(client, "sudo apt-get install -y git")
    run_command_on_instance(client, "sudo apt-get install docker-compose -y")
    run_command_on_instance(client, f"mkdir {project_name}")
    run_command_on_instance(client, f"cd {project_name} ; git clone {git}")
    run_command_on_instance(client, f'cd {project_name}/{git_dir}/{path} ; sudo sed -i "s/dummy_password/{password}/g" docker-compose.yml')
    run_command_on_instance(client, f"cd {project_name}/{git_dir}/{path} ; sudo docker-compose build")
    run_command_on_instance(client, f"cd {project_name}/{git_dir}/{path} ; sudo docker-compose up -d")
    client.close()
    logging.info(f"# run_create_script end \n")

def start_app(ip:str, rsa_key_path:str):
    logging.info(f"# run_start_script {ip}\n")

    rsa_key: paramiko.rsakey.RSAKey = paramiko.rsakey.RSAKey.from_private_key_file(rsa_key_path)
    client: paramiko.SSHClient = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for i in range(3):
        try:
            client.connect(ip, username="ubuntu", pkey=rsa_key)
            break
        except:
            pass
        time.sleep(6)
        logging.info(f"RETRY CONNECT {i+1}")

    logging.info(f"# run_start_script connected \n")
    run_command_on_instance(client, f"cd {project_name}/{git_dir}/{path} ; git checkout HEAD docker-compose.yml")
    run_command_on_instance(client, f'cd {project_name}/{git_dir}/{path} ; sed -i "s/dummy_password/{password}/g" docker-compose.yml')
    run_command_on_instance(client, f"cd {project_name}/{git_dir}/{path} ; sudo docker-compose build")
    run_command_on_instance(client, f"cd {project_name}/{git_dir}/{path} ; sudo docker-compose up -d")
    client.close()
    logging.info(f"# run_start_script end \n")

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], ":hcdgs", ["help", "create","delete","get","start","stop", "init"])
    except getopt.GetoptError as err:
        raise err

    opts = [("-h")] if len(opts) == 0 else opts

    try:
        ec2_client:ec2.Client = boto3.client("ec2")
        network:AWSNetwork = AWSNetwork(ec2_client, project_name=project_name, ports=ports, vpc_cidr_block=vpc_cidr_block, subnet_cidr_block=subnet_cidr_block)
        instance:AWSInstance = AWSInstance(ec2_client, project_name=project_name, instance_type=instance_type, image_id=image_id)
    except:
        logging.info(f"# Require `aws configure` \n")

    for o, a in opts:
        if o in ("-c", "--create"):
            logging.info(f"# CREATE INSTANCE\n")
            ip_list = get_ip(ec2_client, project_name)
            if len(ip_list) > 0:
                logging.info(f"FAILED AT ALREADY EXIST {project_name}")
                exit
            create_network(network)
            create_instance(instance, network)
            file = open(f'{project_name}.pem', "w")
            file.write(instance.pem_data)
            file.flush()
            file.close()
            logging.info(f"# WAIT BY RUNNING \n")
            instance.wait_instance_is_running()
            logging.info(f"# INIT INSTANCE\n")
            ip_list = get_ip(ec2_client, project_name)
            if len(ip_list) > 0:
                create_app(ip_list[0],f"{project_name}.pem")
            else:
                logging.info(f">> Not Found \n")
        elif o in ("-d", "--delete"):
            logging.info(f"# DELETE INSTANCE\n")
            delete_instance(instance)
            logging.info(f"# WAIT BY TERMINATED \n")
            instance.wait_instance_is_terminated()
            delete_network(network)
        elif o in ("-g","--get"):
            print(get_inst(ec2_client, project_name))
        elif o in ("-i","--init"):
            logging.info(f"# INIT INSTANCE\n")
            ip_list = get_ip(ec2_client, project_name)
            if len(ip_list) > 0:
                create_app(ip_list[0],f"{project_name}.pem")
            else:
                logging.info(f">> Not Found \n")
        elif o in ("-s","--stop"):
            logging.info(f"# STOP \n")
            stop_running_instance(ec2_client, project_name)
        elif o in ("-s","--start"):
            logging.info(f"# START \n")
            start_stopped_instance(ec2_client, project_name)
            instance.wait_instance_is_running()
            ip_list = get_ip(ec2_client, project_name)
            if len(ip_list) > 0:
                start_app(ip_list[0],f"{project_name}.pem")
            else:
                logging.info(f">> Not Found \n")
        else:
            print(f"[how to use]")
            print(f"python main.py --create ")
            print(f"python main.py --delete ")




