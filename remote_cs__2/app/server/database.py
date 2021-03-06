import threading
import dataset
import sqlalchemy
from typing import Dict, List
import os
import re
from Crypto.Cipher import AES
import base64
from server.common import encrypt, decrypt
from server.user import User
from server.instance_info import InstanceInfo
import re

class AppDatabase:

    def __init__(self):
        self._db_map: Dict[str, dataset.Database]= {}
        self._lock: threading.Lock = threading.Lock()
        
    def get_db(self):
        key = str(threading.get_ident())
        db = self._db_map.get(key,None)
        if db != None:
            return db
        self._db_map[key] = dataset.connect('sqlite:///mydatabase.db')
        return self._db_map[key]

    def setup(self):
        db: dataset.Database = self.get_db()
        system_table = db.get_table("system")
        if None == system_table.find_one(key = "system_00"):
            system_table:dataset.Table = db.create_table("system")
            system_table.create_column("key",sqlalchemy.VARCHAR(256))
            system_table.create_column("value",sqlalchemy.VARCHAR(256))
            system_table.insert({
                "key":"system_00",
                "value":True})
        User.setup(db)
        InstanceInfo.setup(db)

    def init_app(self, email: str, password:str):
        db: dataset.Database = self.get_db()
        system_table = db.get_table("system")
        if None == system_table.find_one(key = "app_00"):
            user: User = User()
            user._email = email
            user._name = re.sub(r"@.*$", "", email)
            user._password = password
            self.update_user(user)
            system_table.insert({
                "key":"app_00",
                "value":True})
            return True
        else:
            return False

    def get_user_info_from_email(self, email:str) -> User:
        return User.find_one_from_email(self.get_db(), email)

    def update_user(self, user: User):
        user.update(self.get_db())

    def update_instance_info(self, instance_info: InstanceInfo):
        instance_info.save(self.get_db())

    def find_instance_info(self,user_id:str) -> List[InstanceInfo]:
        return InstanceInfo.find_instance_info(self.get_db(), user_id)

    def delete_instance_info(self, name:str):
        InstanceInfo.delete_from_name(self.get_db(),name)