from flask import Flask, request
from flask_httpauth import HTTPDigestAuth
import threading
import dataset
import sqlalchemy
from typing import Dict, List
import os
import re
from server.instance_info import InstanceInfo
from ec2_creator.network import Network

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key here'
auth = HTTPDigestAuth()
db_map:Dict[str, dataset.Database]= {}
root_dir = "/works/app"

lock:threading.Lock = threading.Lock()

def get_db():
    key = str(threading.get_ident())
    db = db_map.get(key,None)
    if db != None:
        return db
    db_map[key] = dataset.connect('sqlite:///mydatabase.db')
    return db_map[key]

def get_username():
    auth_info = request.headers.get("Authorization")
    #
    # replace
    matched = re.match(r'.*username[ ]*=[ ]*"([^"]+)".*',auth_info)
    username = matched.groups()[0]
    return username

def get_user(email:str):
    db:dataset.Database = get_db()
    user_table:dataset.Table = db.create_table("users")
    user = user_table.find_one(email=email)
    return user

def get_user_secret_info(user_id:str):
    db:dataset.Database = get_db()
    user_secret_infos_table:dataset.Table = db.create_table("user_secret_infos")
    user_secret_info = user_secret_infos_table.find_one(user_id=user_id)
    return user_secret_info

@auth.get_password
def get_password(email):
    db:dataset.Database = get_db()
    user_table:dataset.Table = db.create_table("users")
    user = user_table.find_one(email=email)
    if user != None:
        print("--> {}".format(user))
        print("--> {}".format(user.get("password")))
        return user.get("password")
    return None

@app.route('/users.secret_info', methods=['POST', 'GET'])
@auth.login_required
def update_secret_info():
    username = get_username()
    user = get_user(username)
    access_key_id = request.form.get('access_key_id', '')
    secret_key = request.form.get('secret_key', '')
    region = request.form.get('region', '')
    db:dataset.Database = get_db()
    user_secret_info_table:dataset.Table = db.get_table("user_secret_infos")
    print("==>{}".format(
        {
        "user_id":user["id"], 
        "access_key_id":access_key_id,
        "secret_key":secret_key,
        "region":region}
    ))
    user_secret_info_table.update({
        "user_id":user["id"], 
        "access_key_id":access_key_id,
        "secret_key":secret_key,
        "region":region},"user_id")
    return index()

@app.route('/insts.new', methods=['POST', 'GET'])
@auth.login_required
def new_instance():
    username = get_username()
    user = get_user(username)
    db:dataset.Database = get_db()
    user_secret_info_table:dataset.Table = db.get_table("user_secret_infos")
    secret_info = user_secret_info_table.find_one(user_id=user["id"])
    access_key_id = secret_info.get('access_key_id', '')
    secret_key = secret_info.get('secret_key', '')
    region = secret_info.get('region', '')
    name = request.form.get('name','')
    vpc_cidr_block = request.form.get('vpc_cidr_block','')
    subnet_cidr_block = request.form.get('subnet_cidr_block','')
    instance_type = request.form.get('instance_type','')
    image_type = request.form.get('image_type','')

    db:dataset.Database = get_db()
    instance_info:InstanceInfo = InstanceInfo()
    instance_info.name = name
    instance_info.image_type = image_type
    instance_info.instance_type = instance_type
    instance_info.vpc_cidr_block = vpc_cidr_block
    instance_info.subnet_cidr_block = subnet_cidr_block
    instance_info.status = "start"
    instance_info.save(db)

    network:Network = Network(access_key_id=access_key_id.strip(),secret_key=secret_key.strip())
    network.name = name
    network.vpc_cidr_block = vpc_cidr_block
    network.subnet_cidr_block = subnet_cidr_block
    def run():
        network.create_network()
        
    threading.Thread(target=run).start()
    print("=========>{}".format(instance_info.to_dict()))
    print("=========>{}".format(access_key_id))
    print("=========>{}".format(secret_key))
    
    
    
    return index()

@app.route('/', methods=['GET'])
@auth.login_required
def index():
    with open(os.path.join(root_dir,'index.html'),"rb") as f:
        username = get_username()
        user = get_user(username)
        user_secret_info = get_user_secret_info(user["id"])
        print("-->{}".format(user_secret_info))
        cont:str = f.read().decode("utf-8")
        cont = cont.replace("{{username}}",username)
        cont = cont.replace("{{access_key_id}}",user_secret_info["access_key_id"])
        cont = cont.replace("{{secret_key}}",user_secret_info["secret_key"])
        cont = cont.replace("{{region}}",user_secret_info["region"])
        return cont

def setup():
    db:dataset.Database = get_db()
    system_table = db.get_table("system")
    if None != system_table.find_one(key = "initialzied"):
        return

    system_table:dataset.Table = db.create_table("system")
    system_table.create_column("key",sqlalchemy.VARCHAR(256))
    system_table.create_column("value",sqlalchemy.VARCHAR(256))

    user_table:dataset.Table = db.create_table("users")
    user_table.create_column("name",sqlalchemy.VARCHAR(256))
    user_table.create_column("email",sqlalchemy.VARCHAR(256))
    user_table.create_column("password",sqlalchemy.VARCHAR(256))

    user_secret_info_table:dataset.Table = db.create_table("user_secret_infos")
    user_secret_info_table.create_column("user_id",sqlalchemy.VARCHAR(256))
    user_secret_info_table.create_column("access_key_id",sqlalchemy.VARCHAR(512))
    user_secret_info_table.create_column("secret_key",sqlalchemy.VARCHAR(512))
    user_secret_info_table.create_column("region",sqlalchemy.VARCHAR(512))


    InstanceInfo.setup_db(db)
    user_table.insert({
        "name":"kyorohiro",
        "email":"kyorohiro@gmail.com",
        "password":"momonga4110"})

    system_table.insert({
        "key":"initialzied",
        "value":"true"})
    
    user = user_table.find_one(email="kyorohiro@gmail.com")
    user_secret_info_table.insert(
        {
            "user_id":user["id"],
            "access_key_id":"",
            "secret_key":"",
            "region":""
        }
    )
if __name__ == '__main__':
    setup()
    app.run(host="0.0.0.0",port=8080,threaded=True)




