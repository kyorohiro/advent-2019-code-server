import boto3
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
from typing import Dict, List 
import time
instance_name= "advent-code-server"
ec2client:ec2.Client = boto3.client("ec2")


class CodeServerNetwork:

    def __init__(self, ec2_client:ec2.Client, project_name="advent-code-server", ports=[22,8443,8080], vpc_cidr_block='10.1.0.0/16', subnet_cidr_block='10.1.0.0/24'):
        # input
        self._ports = []
        self._ports.extend(ports)
        self._project_name = project_name
        self._vpc_cidr_block = vpc_cidr_block
        self._subnet_cidr_block = subnet_cidr_block
        #
        self._vpc_id:str = ""
        self._route_table_id:str = ""
        self._associate_id:str = ""
        self._gateway_id:str = ""
        self._subnet_id:str = ""
        self._group_id:str = ""
        pass

    @property
    def ports (self):
        return self._ports

    @property
    def project_name (self):
        return self._project_name 

    @property
    def vpc_cidr_block (self):
        return self._vpc_cidr_block 

    @property
    def subnet_cidr_block (self):
        return self._subnet_cidr_block 

    @property
    def vpc_id(self):
        return self._vpc_id

    @property
    def route_table_id(self):
        return self._route_table_id

    @property
    def associate_id(self):
        return self._associate_id

    @property
    def gateway_id(self):
        return self._gateway_id

    @property
    def subnet_id(self):
        return self._subnet_id

    @property
    def group_id(self):
        return self._group_id

    def attach_tag(self, id:str):
        print(">>> ATACH TAG {}".format(id))
        res = ec2client.create_tags(Resources=[id], Tags=[{"Key": "Name", "Value": self._project_name}])
        print("{}".format(res))
    def list_vpc(self):
        res = ec2client.describe_vpcs(Filters=[{"Name":"tag:Name","Values":[self._project_name]}])
        return res

    def create_vpc(self):
        print(">>> CREATE VPC")
        res = ec2client.create_vpc(CidrBlock=self._vpc_cidr_block)
        print("{}".format(res))
        self._vpc_id = vpc_id = res['Vpc']['VpcId']
        self.attach_tag(vpc_id)
        return vpc_id

    def delete_vpc(self, vpc_id=None):
        print(">>> Delete vpcs")
        if vpc_id is None:
            res = ec2client.describe_vpcs(Filters=[{"Name":"tag:Name","Values":[self._project_name]}])
        else:
            res = ec2client.describe_vpcs(Filters=[{"Name":"vpc-id","Values":[vpc_id]}])

        print("{}".format(res))
        for vpc in res["Vpcs"]:
            res = ec2client.delete_vpc(VpcId=vpc['VpcId'])
            print("{}".format(res))

    def create_route_table(self, vpc_id:str):
        res = ec2client.create_route_table(VpcId=vpc_id)
        print("{}".format(res))
        self._route_table_id = route_table_id = res['RouteTable']['RouteTableId']
        self.attach_tag(route_table_id)
        return route_table_id

    def delete_route_table(self, vpc_id=None):
        print(">>> Delete Route Table")
        if vpc_id == None:
            res = ec2client.describe_route_tables(Filters=[{"Name":"tag:Name","Values":[self._project_name]}])
        else:
            res = ec2client.describe_route_tables(Filters=[{"Name":"vpc-id","Values":[vpc_id]}])

        print("{}".format(res))
        for route_table in res["RouteTables"]:
            associations = route_table.get('Associations',[])
            associations_with_main = [a for a in associations if a.get('Main',False)]
            if len(associations_with_main) > 0:
                continue
            for association in associations:
                if association.get('Main',False):
                    # infnore main table
                    continue
                ec2client.disassociate_route_table(AssociationId = association['RouteTableAssociationId'])
            res = ec2client.delete_route_table(RouteTableId=route_table['RouteTableId'])
            print("{}".format(res))

    def create_route(self, route_table_id:str, gateway_id:str):
        resp = ec2client.create_route(RouteTableId=route_table_id,DestinationCidrBlock="0.0.0.0/0",GatewayId=gateway_id)
        print("{}".format(resp))

    def delete_route(self, vpc_id=None):
        if vpc_id == None:
            res = ec2client.describe_route_tables(Filters=[{"Name":"tag:Name","Values":[self._project_name]}])
        else:
            res = ec2client.describe_route_tables(Filters=[{"Name":"vpc-id","Values":[vpc_id]}])     
        print("{}".format(res))
        for route_table in res["RouteTables"]:
            resp = ec2client.delete_route(DestinationCidrBlock="0.0.0.0/0",RouteTableId=route_table['RouteTableId'])
            print("{}".format(resp))

    def associate_route_table(self, route_table_id:str, subnet_id:str):
        res = ec2client.associate_route_table(RouteTableId=route_table_id,SubnetId=subnet_id)
        print("{}".format(res))
        self._associate_id = associate_id = res['AssociationId']
        return associate_id


    def create_gateway(self, vpc_id:str):
        print(">>> CREATE GATEWAY")
        res = ec2client.create_internet_gateway()
        print("{}".format(res))
        self._gateway_id = gateway_id = res['InternetGateway']['InternetGatewayId']
        self.attach_tag(gateway_id)

        print(">>> ATTACH GATEWAY")
        res = ec2client.attach_internet_gateway(InternetGatewayId=gateway_id,VpcId=vpc_id)
        print("{}".format(res))
        return gateway_id

    def delete_gateway(self, vpc_id=None):
        print(">> Detach Gateway")
        if vpc_id is not None:
            if vpc_id is None:
                res = ec2client.describe_internet_gateways(Filters=[{"Name":"tag:Name","Values":[self._project_name]}])
            else:
                res = ec2client.describe_internet_gateways(Filters=[{"Name":"attachment.vpc-id","Values":[vpc_id]}])
            print("{}".format(res))
            for  gateway in res['InternetGateways']:
                res = ec2client.detach_internet_gateway(InternetGatewayId=gateway['InternetGatewayId'],VpcId=vpc_id)
                print("{}".format(res))

        if vpc_id is None:
            res = ec2client.describe_internet_gateways(Filters=[{"Name":"tag:Name","Values":[self._project_name]}])
        else:
            res = ec2client.describe_internet_gateways(Filters=[{"Name":"attachment.vpc-id","Values":[vpc_id]}])
        print(">> Delete Gateway")
        for gateway in res['InternetGateways']:
            res = ec2client.delete_internet_gateway(InternetGatewayId=gateway['InternetGatewayId'])
            print("{}".format(res))

    def create_subnet(self, vpc_id:str):
        print(">>> CREATE SUBNET")
        res = ec2client.create_subnet(CidrBlock=self._subnet_cidr_block ,VpcId=vpc_id)
        print("{}".format(res))
        self._subnet_id = subnet_id = res['Subnet']['SubnetId']
        self.attach_tag(subnet_id)
        return subnet_id

    def delete_subnet(self, vpc_id=None):
        print(">> Delete subnet")
        if vpc_id is None:
            res = ec2client.describe_subnets(Filters=[{"Name":"tag:Name","Values":[self._project_name]}])
        else:
            res = ec2client.describe_subnets(Filters=[{"Name":"vpc-id","Values":[vpc_id]}])

        print("{}".format(res))
        for subnet in res["Subnets"]:
            res = ec2client.delete_subnet(SubnetId=subnet['SubnetId'])
            print("{}".format(res))

    def create_security_group(self, vpc_id):
        print(">>> CREATE SECURITY GROUP")
        res = ec2client.create_security_group(Description="AdventCodeServer",GroupName=self._project_name,VpcId=vpc_id)
        print("{}".format(res))
        self._group_id = group_id = res['GroupId']
        self.attach_tag(group_id)
        return group_id

    def delete_security_group(self, vpc_id=None):
        if vpc_id is None:
            res = ec2client.describe_security_groups(Filters=[{"Name":"tag:Name","Values":[self._project_name]}])
        else:
            res = ec2client.describe_security_groups(Filters=[{"Name":"vpc-id","Values":[vpc_id]}])
        print("{}".format(res))
        for sg in res['SecurityGroups']:
            if sg.get('GroupName','default') == 'default':
                # ignore defalut 
                continue
            res = ec2client.delete_security_group(GroupId=sg["GroupId"])
            print("{}".format(res))

    def create_security_group_ingress(self, group_id):
        print(">>>> CREATE SECURITY GROUP INGRESS")
        ip_permissions = []
        for port in self._ports:
            ip_permissions.append(
                {
                    'IpProtocol': 'tcp',
                    'FromPort': port,
                    'ToPort': port,
                    'IpRanges':[
                        {'CidrIp': '0.0.0.0/0', 'Description' : f'{port}'}
                    ]
                }
            )
        
        res = ec2client.authorize_security_group_ingress(
            GroupId=group_id, IpPermissions=ip_permissions)
        print("{}".format(res))


