import threading
import dataset
import sqlalchemy
from typing import Dict, List
import os
import re
from Crypto.Cipher import AES
import base64
from server.common import *

class User:
    """
    User 情報
    - ログイン用の情報
    - AWS へ アクセスするための情報
    """
    def __init__(self):
        self._id = None
        self._email = ""
        self._name = ""
        self._password = ""
        self._aws_access_key_id = ""
        self._aws_secret_key = ""
        self._aws_region = ""


    @property
    def id(self):
        return self._id

    @property
    def email(self):
        return self._email

    @property
    def name(self):
        return self._name

    @property
    def password(self):
        return self._password

    @property
    def aws_access_key_id(self):
        return self._aws_access_key_id

    @property
    def aws_secret_key(self):
        return self._aws_secret_key

    @property
    def aws_region(self):
        return self._aws_region

    @classmethod
    def setup(self, db: dataset.Database):
        system_table = db.get_table("system")
        if None == system_table.find_one(key = "user_00"):
                user_table:dataset.Table = db.create_table("users")
                user_table.create_column("name",sqlalchemy.VARCHAR(256))
                user_table.create_column("email",sqlalchemy.VARCHAR(256))
                user_table.create_column("password",sqlalchemy.VARCHAR(256))

                user_table.insert({
                    "name":"kyorohiro",
                    "email":"kyorohiro@gmail.com",
                    "password": encrypt("password (0_0)")})
                system_table.insert({
                    "key":"user_00",
                    "value":True})

        if None == system_table.find_one(key = "user_01"):
                user_table:dataset.Table = db.create_table("users")
                user_table.create_column("aws_access_key_id", sqlalchemy.VARCHAR(512))
                user_table.create_column("aws_secret_key", sqlalchemy.VARCHAR(512))
                user_table.create_column("aws_region", sqlalchemy.VARCHAR(256))

                system_table.insert({
                    "key":"user_01",
                    "value":True})
    
    @classmethod
    def create_empty_user(cls):
        return User()

    @classmethod
    def find_one_from_email(cls, db: dataset.Database, email: str):
        user_table: dataset.Table = db.create_table("users")
        print(f"{[u for u in user_table.find()]}")
        _user = user_table.find_one(email=email)

        if _user == None:
            return User.create_empty_user()

        user = User()
        user._id = _user.get("id", None)
        user._name = _user.get("name", "")
        user._email = _user.get("email", "")
        user._password = decrypt(_user.get("password", ""))
        user._aws_access_key_id = decrypt(_user.get("aws_access_key_id", ""))
        user._aws_secret_key = decrypt(_user.get("aws_secret_key", ""))
        user._aws_region = decrypt(_user.get("aws_region", ""))
        return user

    def update(self, db: dataset.Database):
        user_table: dataset.Table = db.create_table("users")
        user_table.update({
            "email": self._email,
            "name": self._name,
            "password": encrypt(self._password),
            "aws_access_key_id": encrypt(self._aws_access_key_id),
            "aws_secret_key": encrypt(self._aws_secret_key),
            "aws_region": encrypt(self._aws_region)}, ['email'])

