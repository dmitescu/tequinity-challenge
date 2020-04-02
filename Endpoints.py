from flask import Flask, Response
from flask import request

from flask_sockets import Sockets

from flask_argon2 import Argon2

from werkzeug.middleware.proxy_fix import ProxyFix

from Auth import auth_rest_endpoint, auth_socket, Auth
from User import User
from Text import Text
from ParsingRequest import ParsingRequest

from Database import init_db, db_session

import time
import json

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:////tmp/test.db"

sockets = Sockets(app)
Argon = Argon2(app)
init_db()

@app.route("/register", methods=['POST'])
def register():
    body = request.get_json()
    if body is None:
        return Response(status=400)
    user = body['username']
    passwd = body['password']
    if user is None or passwd is None:
        return Response(status=400)
    u = User(user,passwd)
    
    db_session.add(u)
    db_session.commit()
    
    return Response(status=200)

@app.route("/auth", methods=['POST'])
def auth():
    body = request.get_json()
    if body is None:
        return Response(status=400)
    user = body['username']
    passwd = body['password']
    if user is None or passwd is None:
        return Response(status=400)
    found_user = User.query.filter(User.username == user).first()
    if found_user is None:
        return Response(status=403)
    if Argon.check_password_hash(found_user.hsh, passwd + found_user.salt):
        auth = Auth()

        db_session.add(auth)
        db_session.commit()
        
        resp = Response(status=400)
        resp.headers["X-Auth-Token"] = auth.token
        return resp
    return Response(status=403)

@app.route("/upload", methods=['POST'])
@auth_rest_endpoint
def upload():
    body = request.get_json()
    if body is None:
        return Response(status=400)
    text = body['text']
    if text is None:
        return Response(status=400)
    already_exists = Text.query.filter(Text.text == text).first()
    if already_exists:
        return Response(json.dumps({"id":already_exists.id}),status=200)
    else:
        text_entity = Text(text)
        db_session.add(text_entity)
        db_session.commit()
        text_entity = Text.query.filter(Text.text == text).first()
        return Response(json.dumps({"id":text_entity.id}),status=200)        

@app.route("/parse", methods=['POST'])
@auth_rest_endpoint
def parse():
    body = request.get_json()
    if body is None:
        return Response(status=400)
    text_id = body['text_id']
    if text_id is None:
        return Response(status=400)

    found_text = Text.query.filter(Text.id == text_id).first()

    if found_text is None:
        return Response(status=400)

    parsing_request = ParsingRequest(found_text.text)
    parsing_result = parsing_request.get_result()

    return Response(parsing_result.to_json(), status=200)

@sockets.route("/echo")
@auth_socket
def echo_socket(ws):
    while not ws.closed:
        body_unparsed = ws.receive()

        try:
            body = json.loads(body_unparsed)
        except json.decoder.JSONDecodeError:
            ws.send(json.dumps({"status":"error"}))
            return

        text_id = body["text_id"]
        text = body["text"]

        if text:
            already_exists = Text.query.filter(Text.text == text).first()
            if already_exists:
                ws.send(json.dumps({"id":already_exists.id}))
            else:
                text_entity = Text(text)
                db_session.add(text_entity)
                db_session.commit()
                text_entity = Text.query.filter(Text.text == text).first()
                ws.send(json.dumps({"id":text_entity.id}))
        if text_id:
            found_text = Text.query.filter(Text.id == text_id).first()

            if found_text is None:
                return Response(status=400)

            parsing_request = ParsingRequest(found_text.text)
            parsing_result = parsing_request.get_result()

            ws.send(parsing_result.to_json())
        ws.send(json.dumps({"status":"error"}))
        
@app.route("/health", methods=['GET'])
def health():
    return Response(status=200)

if __name__ == '__main__':
    socketio.run(app)
    
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
