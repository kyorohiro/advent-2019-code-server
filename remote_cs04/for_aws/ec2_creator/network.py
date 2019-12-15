import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
import json
import time
from typing import Dict, List 



class Network:

    def __init__(self):
        self._name = "advent-code-server"
        self._vpc_cidr_block = '10.1.0.0/16'
        self._subnet_cidr_block = '10.1.0.0/24'
        self._tcp_ports = [8443,8080,22]
        self._udp_ports = [8443,8080,22]
        self._vpc_id:str = None
        self._gateway_id:str = None 
        self._route_table_id:str = None
        self._subnet_id:str = None
        self._ec2client:ec2.Client = boto3.client("ec2")

    def to_dict(self):
        return {
            "name" : self._name,
            "vpc_cidr_block" : self._vpc_cidr_block,
            "subnet_cidr_block" : self._subnet_cidr_block,
            "tcp_ports" : self._tcp_ports,
            "udp_ports" : self._udp_ports,
            "vpc_id" : self._vpc_id,
            "gateway_id" : self._gateway_id,
            "route_table_id" : self._route_table_id,
            "subnet_id" : self._subnet_id
        }

    @property
    def name(self) -> str:
        return self._name

    @property
    def vpc_cidr_block(self) -> str:
        return self._vpc_cidr_block

    @property
    def subnet_cidr_block(self) -> str:
        return self._subnet_cidr_block

    @property
    def tcp_ports(self) -> List[int]:
        return self._tcp_ports
    
    @property
    def udp_ports(self) -> List[int]:
        return self._udp_ports

    def create_vpc(self):
        print(">>> CREATE VPC")
        res = self._ec2client.create_vpc(CidrBlock=self.vpc_cidr_block)
        print("{}".format(res))
        self._vpc_id = res['Vpc']['VpcId']
        res = self._ec2client.create_tags(Resources=[self._vpc_id], Tags=[{"Key": "Name", "Value": self._name}])
        print("{}".format(res))
    
    def create_gateway(self):
        print(">>> CREATE GATEWAY")
        res = self._ec2client.create_internet_gateway()
        print("{}".format(res))
        self._gateway_id = res['InternetGateway']['InternetGatewayId']
        res = self._ec2client.create_tags(Resources=[self._gateway_id], Tags=[{"Key": "Name", "Value": self._name}])
        print("{}".format(res))

        res = self._ec2client.attach_internet_gateway(InternetGatewayId=self._gateway_id,VpcId=self._vpc_id)
        print("{}".format(res))

    def create_route_table(self):
        print(">>> CREATE ROUTE TABLE")
        res = self._ec2client.create_route_table(VpcId=self._vpc_id)
        print("{}".format(res))
        self._route_table_id = res['RouteTable']['RouteTableId']
        res = self._ec2client.create_tags(Resources=[self._route_table_id], Tags=[{"Key": "Name", "Value": self._name}])
        print("{}".format(res))

    def create_subnet(self):
        print(">>> CREATE SUBNET")
        res = self._ec2client.create_subnet(CidrBlock='10.1.0.0/24',VpcId=self._vpc_id)
        self._subnet_id = res['Subnet']['SubnetId']
        res = self._ec2client.create_tags(Resources=[self._subnet_id], Tags=[{"Key": "Name", "Value": self._name}])
        print("{}".format(res))

    def create_security_group(self):
        print(">>> CREATE SECURITY GROUP")
        res = self._ec2client.create_security_group(Description="AdventCodeServer",GroupName=self._name)
        print("{}".format(res))
        self._group_id = res['GroupId']
        res = self._ec2client.create_tags(Resources=[self._group_id], Tags=[{"Key": "Name", "Value": self._name}])
        print("{}".format(res))

    def create_security_group_ingress(self):
        print(">>>> CREATE SECURITY GROUP INGRESS")
        ip_permissions = []
        for port in self._tcp_ports:
            ip_permissions.append(
                {
                    'IpProtocol': 'tcp',
                    'FromPort': port,
                    'ToPort': port,
                    'IpRanges':[
                        {'CidrIp': '0.0.0.0/0', 'Description' : f'${port}'}
                    ]
                }
            )
        for port in self._udp_ports:
            ip_permissions.append(
                {
                    'IpProtocol': 'udp',
                    'FromPort': port,
                    'ToPort': port,
                    'IpRanges':[
                        {'CidrIp': '0.0.0.0/0', 'Description' : f'${port}'}
                    ]
                }
            )
        res = self._ec2client.authorize_security_group_ingress(
                GroupName="{}".format(self._name), IpPermissions=ip_permissions)
        print("{}".format(res))

    def create_network(self):
        file = open("network_info_{}_{}.json".format(self._name, time.time()),"w")
        file.write("")
        network_info = {}
        try:
            self.create_vpc()
            self.create_gateway()
            self.create_route_table()
            self.create_subnet()
            self.create_security_group()
            self.create_security_group_ingress()
        finally:
            file.write(json.dumps(self.to_dict()))
            file.close()

        return network_info