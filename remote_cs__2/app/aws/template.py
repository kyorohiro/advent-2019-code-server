from aws.network import AWSNetwork
from aws.instance import AWSInstance
from typing import List
from boto3_type_annotations.ec2 import Client as EC2Client
def create_network(network:AWSNetwork):
    print(">>> Create")
    try:
        vpc_id:str = network.create_vpc()
        gateway_id:str = network.create_gateway(vpc_id)
        subnet_id:str = network.create_subnet(vpc_id)
        group_id:str = network.create_security_group(vpc_id)
        network.create_security_group_ingress(group_id)
        route_table_id:str = network.create_route_table(vpc_id)
        network.create_route(route_table_id, gateway_id)
        network.associate_route_table(route_table_id, subnet_id)
    except :
        pass
    return network

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


def create_instance(instance:AWSInstance, network:AWSNetwork):
    instance.create_pem()
    instance.create_instance(subnet_id=network.subnet_id, group_id=network.group_id)

def delete_instance(instance:AWSInstance):
    instance.delete_pem()
    instance.delete_instance()

def get_ip(ec2_client: EC2Client, project_name) -> List[str]:
    print(">>>> ec2client.describe_instances")
    res = ec2_client.describe_instances(Filters=[{"Name":"tag:Name","Values":[project_name]}])
    print("{}".format(res))
    ip_list: List[str] = []
    for reserve_info in res['Reservations']:
        for instance_info in reserve_info['Instances']:
            if "running" == instance_info.get('State',{}).get("Name",""):
                ip = instance_info.get('PublicIpAddress', None)
                if ip is not None:
                    ip_list.append(ip)
    return ip_list

def get_inst(ec2_client: EC2Client, project_name) -> str:
    strs: List[str] = []
    try:
        print(">>>> ec2client.describe_instances")
        res = ec2_client.describe_instances(Filters=[{"Name":"tag:Name","Values":[project_name]}])
        print("{}".format(res))

        for reserve_info in res['Reservations']:
            strs.append("-")
            for instance_info in reserve_info['Instances']:
                strs.append(">>>> {}".format(instance_info.get('InstanceId',"")))
                strs.append(">>>> {}".format(instance_info.get('PublicDnsName',"")))
                strs.append(">>>> {}".format(instance_info.get('PublicIpAddress',"")))
                strs.append(">>>> {}".format(instance_info.get('PrivateDnsName',"")))
                strs.append(">>>> {}".format(instance_info.get('PrivateIpAddress',"")))
                strs.append(">>>> {}".format(instance_info.get('State',"")))
    except Exception as e:
        strs.append("-- {}".format(e.args))
    return "\n".join(strs)

def stop_running_instance(ec2_client: EC2Client, project_name) -> List[str]:
    print(">>>> ec2client.describe_instances")
    res = ec2_client.describe_instances(Filters=[{"Name":"tag:Name","Values":[project_name]}])
    print("{}".format(res))
    ip_list: List[str] = []
    for reserve_info in res['Reservations']:
        for instance_info in reserve_info['Instances']:
            if "running" == instance_info.get('State',{}).get("Name",""):
                ec2_client.stop_instances(InstanceIds=[instance_info['InstanceId']])
                ip = instance_info.get('PublicIpAddress', None)
                if ip is not None:
                    ip_list.append(ip)
    return ip_list

def start_stopped_instance(ec2_client: EC2Client, project_name) -> List[str]:
    print(">>>> ec2client.describe_instances")
    res = ec2_client.describe_instances(Filters=[{"Name":"tag:Name","Values":[project_name]}])
    print("{}".format(res))
    ip_list: List[str] = []
    for reserve_info in res['Reservations']:
        for instance_info in reserve_info['Instances']:
            if "stopped" == instance_info.get('State',{}).get("Name",""):
                ec2_client.start_instances(InstanceIds=[instance_info['InstanceId']])
                ip = instance_info.get('PublicIpAddress', None)
                if ip is not None:
                    ip_list.append(ip)
    return ip_list