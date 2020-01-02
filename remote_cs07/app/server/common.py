import threading
import dataset
import sqlalchemy
from typing import Dict, List
import os
import re
from Crypto.Cipher import AES
import base64

CIPHER_KEY: str  = "Drup OnNS c ca gEyA HXD v bK 193"
IV = bytes.fromhex("e90dd0be70e18333783c939cafaf69f5")
BLOCK_SIZE = 32


def decrypt(message:str):
    cipher: AES = AES.new(CIPHER_KEY, AES.MODE_CBC, IV)
    try:
        v = cipher.decrypt(bytes.fromhex(message)).decode('utf-8')
        print(f">>{v}")
        m = re.match(r'([0-9]+):(.+)', v)
        groups = m.groups()
        print(f">>{groups}")
        return groups[1][:int(groups[0])]
    except:
        return ""

def encrypt(message:str):
    cipher: AES = AES.new(CIPHER_KEY, AES.MODE_CBC, IV)
    message = f"{len(message)}:{message}"
    message = message + "." * (BLOCK_SIZE - (len(message) % BLOCK_SIZE))
    return cipher.encrypt(message.encode('utf-8')).hex()
