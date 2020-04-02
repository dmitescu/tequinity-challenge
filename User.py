from sqlalchemy import Column, Integer, String

from Database import Base

import json
import random
import hashlib
import binascii

from sqlalchemy import Column, Integer, String
import Endpoints

alph = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_./"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True)
    salt = Column(String(512), unique=False)
    hsh = Column(String(512), unique=False)
    
    def __init__(self, username, passwd):
        self.username = username
        salt = []
        for i in range(512):
            salt.append(random.choice(alph))
        self.salt = "".join(salt)
        self.hsh = Endpoints.Argon.generate_password_hash(passwd + self.salt)
