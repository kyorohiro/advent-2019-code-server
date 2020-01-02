from flask import Flask, request
from flask_httpauth import HTTPDigestAuth
import threading
import dataset
import sqlalchemy
from typing import Dict, List
import os
import re
import server.database as sv_db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key here'
auth = HTTPDigestAuth()
db_map:Dict[str, dataset.Database]= {}
root_dir = "/works/app"
app_db: sv_db.AppDatabase = sv_db.AppDatabase()

def get_username_from_header():
    auth_info = request.headers.get("Authorization")
    #
    # replace
    matched = re.match(r'.*username[ ]*=[ ]*"([^"]+)".*',auth_info)
    username = matched.groups()[0]
    return username


@auth.get_password
def get_password(email):
    user: sv_db.User = app_db.get_user_info_from_email(email)
    if user != None:
        return user.password
    return None

@app.route('/user_info.update', methods=['POST'])
@auth.login_required
def update_user_info():
    username = get_username_from_header()
    user: sv_db.User = app_db.get_user_info_from_email(username)
    user._password = request.form.get('password', "")
    app_db.update_user(user)
    return index()

@app.route('/aws_info.update', methods=['POST'])
@auth.login_required
def update_aws_info():
    username = get_username_from_header()
    user: sv_db.User = app_db.get_user_info_from_email(username)
    user._aws_access_key_id = request.form.get('aws_access_key_id', "")
    user._aws_secret_key = request.form.get('aws_secret_key', "")
    user._aws_region = request.form.get('aws_region', "")
    app_db.update_user(user)
    return index()

@app.route('/insts.new', methods=['POST', 'GET'])
@auth.login_required
def new_instance():
    pass
    def run():
        pass
    #threading.Thread(target=run).start()
    #print("=========>{}".format(instance_info.to_dict()))
    #print("=========>{}".format(access_key_id))
    #print("=========>{}".format(secret_key))
    
    
    
    return index()

@app.route('/', methods=['GET'])
@app.route('/aws_info.update', methods=['GET'])
@app.route('/user_info.update', methods=['GET'])
@auth.login_required
def index():
    with open(os.path.join(root_dir,'server/index.html'),"rb") as f:
        username = get_username_from_header()
        user: sv_db.User = app_db.get_user_info_from_email(username)
        #print("-->{}".format(user_secret_info))
        cont:str = f.read().decode("utf-8")
        cont = cont.replace("{{username}}",username)
        cont = cont.replace("{{aws_access_key_id}}",user.aws_access_key_id)
        cont = cont.replace("{{aws_secret_key}}",user.aws_secret_key[0:0])
        cont = cont.replace("{{aws_region}}",user.aws_region)
        return cont

def setup():
    app_db.setup()

if __name__ == '__main__':
    setup()
    app.run(host="0.0.0.0",port=8080,threaded=True)




