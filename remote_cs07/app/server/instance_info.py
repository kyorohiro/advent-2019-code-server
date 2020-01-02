import threading
import dataset
import sqlalchemy
from typing import Dict, List
import os
import re
from Crypto.Cipher import AES
import base64
from server.common import *


class InstanceInfo:

    def __init__(self):
        self._name = ""
        self._user_id = ""
        self._vpc_cidr_block = ""
        self._subnet_cidr_block = ""
        self._instance_type = ""
        self._image_type = ""
        self._vpc_id = ""
        self._gateway_id = ""
        self._route_table_id = ""
        self._subnet_id = ""
        self._group_id = ""
        self._key_name = ""
        self._instance_id = ""
        self._pem = ""
        self._status = ""

    def to_dict(self):
        return {
            "name" : self._name,
            "user_id" : self._user_id,
            "vpc_cidr_block" : self._vpc_cidr_block,
            "subnet_cidr_block" : self._subnet_cidr_block,
            "instance_type" : self._instance_type,
            "image_type" : self._image_type,
            "vpc_id" : self._vpc_id,
            "gateway_id" : self._gateway_id,
            "route_table_id" : self._route_table_id,
            "subnet_id" : self._subnet_id,
            "group_id" : self._group_id,
            "key_name" : self._key_name,
            "instance_id" : self._instance_id,
            "pem" : self._pem,
            "status" : self._status
        }

    def save(self, db:dataset.Database):
        table:dataset.Table = db.get_table("instance_infos")
        table.upsert(self.to_dict(), ["user_id", "name"])

    @classmethod
    def find_instance_info(cls, db:dataset.Database, user_id:str):
        user_table: dataset.Table = db.create_table("instance_infos")
        resp = user_table.find(user_id=user_id)
        return [InstanceInfo.create_from_dict(r) for r in resp]

    @classmethod
    def create_from_dict(cls,data: Dict) -> List:
        self: InstanceInfo = InstanceInfo()
        self._name = data.get("name", "")
        self._user_id = data.get("user_id","")
        self._vpc_cidr_block = data.get("vpc_cidr_block","")
        self._subnet_cidr_block = data.get("subnet_cidr_block","")
        self._instance_type = data.get("instance_type","")
        self._image_type = data.get("image_type","")
        self._vpc_id = data.get("vpc_id","")
        self._gateway_id = data.get("gateway_id","")
        self._route_table_id = data.get("route_table_id","")
        self._subnet_id = data.get("subnet_id","")
        self._group_id = data.get("group_id","")
        self._key_name = data.get("key_name","")
        self._instance_id = data.get("instance_id","")
        self._pem = data.get("pem","")
        self._status = data.get("status","")
        return self

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
