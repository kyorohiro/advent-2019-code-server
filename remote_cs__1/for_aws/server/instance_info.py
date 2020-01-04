from flask import Flask, request
from flask_httpauth import HTTPDigestAuth
import threading
import dataset
import sqlalchemy
from typing import Dict, List
import os
import re

from ec2_creator.instance import Instance
from ec2_creator.network import Network

class InstanceInfo:
    def __init__(self):
        self.name = ""
        self.user_id = ""
        self.vpc_cidr_block = ""
        self.subnet_cidr_block = ""
        self.instance_type = ""
        self.image_type = ""
        self.vpc_id = ""
        self.gateway_id = ""
        self.route_table_id = ""
        self.subnet_id = ""
        self.group_id = ""
        self.key_name = ""
        self.instance_id = ""
        self.pem = ""
        self.status = ""

    def to_dict(self):
        return {
            "name" : self.name,
            "user_id" : self.user_id,
            "vpc_cidr_block" : self.vpc_cidr_block,
            "subnet_cidr_block" : self.subnet_cidr_block,
            "instance_type" : self.instance_type,
            "image_type" : self.image_type,
            "vpc_id" : self.vpc_id,
            "gateway_id" : self.gateway_id,
            "route_table_id" : self.route_table_id,
            "subnet_id" : self.subnet_id,
            "group_id" : self.group_id,
            "key_name" : self.key_name,
            "instance_id" : self.instance_id,
            "pem" : self.pem,
            "status" : self.status
        }

    def save(self, db:dataset.Database):
        table:dataset.Table = db.get_table("instance_infos")
        table.upsert(self.to_dict(), ["user_id", "name"])

    @classmethod
    def setup_db(cls, db:dataset.Database):
        instance_info_table:dataset.Table = db.create_table("instance_infos")
        instance_info_table.create_column("user_id", sqlalchemy.VARCHAR(256))
        instance_info_table.create_column("name", sqlalchemy.VARCHAR(512))
        instance_info_table.create_column("vpc_cidr_block", sqlalchemy.VARCHAR(64))
        instance_info_table.create_column("subnet_cidr_block", sqlalchemy.VARCHAR(64))
        instance_info_table.create_column("instance_type", sqlalchemy.VARCHAR(64))
        instance_info_table.create_column("image_type", sqlalchemy.VARCHAR(64))
        instance_info_table.create_column("vpc_id", sqlalchemy.VARCHAR(128))
        instance_info_table.create_column("gateway_id", sqlalchemy.VARCHAR(128))
        instance_info_table.create_column("route_table_id", sqlalchemy.VARCHAR(128))
        instance_info_table.create_column("subnet_id", sqlalchemy.VARCHAR(128))
        instance_info_table.create_column("group_id", sqlalchemy.VARCHAR(128))
        instance_info_table.create_column("key_name", sqlalchemy.VARCHAR(128))
        instance_info_table.create_column("instance_id", sqlalchemy.VARCHAR(128))
        instance_info_table.create_column("pem", sqlalchemy.TEXT)
        instance_info_table.create_column("status", sqlalchemy.VARCHAR(64))
