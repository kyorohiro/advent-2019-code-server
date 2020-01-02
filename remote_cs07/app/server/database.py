import threading
import dataset
import sqlalchemy
from typing import Dict, List
import os
import re
from Crypto.Cipher import AES
import base64
from server.common import *
from server.user import User


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

    def get_user_info_from_email(self, email:str) -> User:
        return User.find_one_from_email(self.get_db(), email)

    def update_user(self, user: User):
        user.update(self.get_db())

