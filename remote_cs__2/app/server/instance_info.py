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
        self._associate_id = ""
        self._group_id = ""
        self._key_name = ""
        self._instance_id = ""
        self._pem = ""
        self._status = ""
        self._ports = []
        self._git = ""
        self._path = ""
        self._sh = ""

    @property
    def name(self):
        return self._name
    @property
    def user_id(self):
        return self._user_id
    @property
    def vpc_cidr_block(self):
        return self._vpc_cidr_block
    @property
    def subnet_cidr_block(self):
        return self._subnet_cidr_block
    @property
    def instance_type(self):
        return self._instance_type
    @property
    def image_type(self):
        return self._image_type
    @property
    def vpc_id(self):
        return self._vpc_id
    @property
    def gateway_id(self):
        return self._gateway_id
    @property
    def route_table_id(self):
        return self._route_table_id
    @property
    def subnet_id(self):
        return self._subnet_id
    @property
    def associate_id(self):
        return self._associate_id
    @property
    def group_id(self):
        return self._group_id
    @property
    def key_name(self):
        return self._key_name
    @property
    def instance_id(self):
        return self._instance_id
    @property
    def pem(self):
        return self._pem
    @property
    def status(self):
        return self._status
    @property
    def ports(self):
        return self._ports

    @property
    def git(self):
        return self._git

    @property
    def path(self):
        return self._path

    @property
    def sh(self):
        return self._sh

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
            "associate_id": self._associate_id,
            "key_name" : self._key_name,
            "instance_id" : self._instance_id,
            "pem" : self._pem,
            "status" : self._status,
            "git" : self._git,
            "path" : self._path,
            "sh" : self._sh
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
        self._associate_id = data.get("associate_id","")
        self._key_name = data.get("key_name","")
        self._instance_id = data.get("instance_id","")
        self._pem = data.get("pem","")
        self._status = data.get("status","")
        self._ports = data.get("ports","")
        self._git = data.get("git","")
        self._path = data.get("path","")
        self._sh = data.get("sh","")
        return self

    @classmethod
    def setup(cls, db:dataset.Database):
        system_table = db.get_table("system")
        if None == system_table.find_one(key = "instance_info_00"):
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
            instance_info_table.create_column("associate_id", sqlalchemy.VARCHAR(128))
            instance_info_table.create_column("pem", sqlalchemy.TEXT)
            instance_info_table.create_column("status", sqlalchemy.VARCHAR(64))
            instance_info_table.create_column("ports", sqlalchemy.VARCHAR(512))
            instance_info_table.create_column("git", sqlalchemy.VARCHAR(512))
            instance_info_table.create_column("path", sqlalchemy.VARCHAR(512))
            instance_info_table.create_column("sh", sqlalchemy.VARCHAR(512))

            system_table.insert({
                    "key": "instance_info_00",
                    "value":True})
    @classmethod
    def delete_from_name(cls, db:dataset.Database, name:str):
        instance_table: dataset.Table = db.create_table("instance_infos")
        instance_table.delete(name=name)
