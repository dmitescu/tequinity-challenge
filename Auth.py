from flask import request
from flask import Flask, Response
from functools import wraps

import random
import json

from sqlalchemy import Column, Integer, String

from Database import init_db, db_session
from Database import Base

alph = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_./"

def auth_rest_endpoint(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        token = request.headers.get("X-Auth-Token")

        found_auth = Auth.query.filter(Auth.token == token).first()

        if found_auth is None:
            return Response(status=403)
        
        return f(*args, **kwds)
    return wrapper

def auth_socket(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        if len(args) < 1:
            raise Exception("no websocket found")
        ws = args[0]

        # TODO add timeout to avoid DOS
        ws.send(json.dumps({"status": "beggining auth"}))
        auth = ws.receive()

        try:
            auth_json = json.loads(auth)
        except json.decoder.JSONDecodeError:
            ws.send(json.dumps({"status": "error"}))
            return

        token = auth_json['X-Auth-Token']

        if token is None:
            ws.send(json.dumps({"status":"unauthenticated"}))
            return

        found_auth = Auth.query.filter(Auth.token == token).first()

        if found_auth is None:
            ws.send(json.dumps({"status":"unathenticated"}))
            return
        
        return f(*args, **kwds)
    return wrapper

class Auth(Base):
    __tablename__ = 'auth'
    id = Column(Integer, primary_key=True)
    token = Column(String(32))

    def __init__(self, token = None):
        if token is None:
            token = []
            for i in range(512):
                token.append(random.choice(alph))
            self.token = "".join(token)
        else:
            self.token = token
