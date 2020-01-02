from flask import Flask, request, render_template
from flask_httpauth import HTTPDigestAuth
import threading
import dataset
import sqlalchemy
from typing import Dict, List
import os
import re
import server.database as sv_db
from server.instance_info import InstanceInfo
from aws.network import AWSNetwork
#
import boto3
import sys, getopt
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError

app = Flask(__name__,template_folder="/works/app/server/templates",static_folder="/works/app/server/statics", static_url_path="/statics")
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

@app.route('/inst.new', methods=['POST'])
@auth.login_required
def new_instance():
    username = get_username_from_header()
    user: sv_db.User = app_db.get_user_info_from_email(username)
    #
    instance_info:InstanceInfo = InstanceInfo()
    instance_info._name = request.form.get('name', "")
    instance_info._vpc_cidr_block = request.form.get('vpc_cidr_block', "")
    instance_info._subnet_cidr_block = request.form.get('subnet_cidr_block', "")
    instance_info._instance_type = request.form.get('instance_type', "")
    instance_info._image_type = request.form.get('image_type', "")
    instance_info._status = "before running"
    instance_info._user_id = user.id
    app_db.update_instance_info(instance_info)

    ec2_client:ec2.Client = boto3.client("ec2", region_name=user.aws_region, 
        aws_access_key_id=user.aws_access_key_id,aws_secret_access_key=user.aws_secret_key)

    def run():
        aws_network:AWSNetwork = AWSNetwork.create_network(ec2_client, project_name=instance_info._name, 
        ports=[22,8443,8080], vpc_cidr_block=instance_info._vpc_cidr_block, subnet_cidr_block=instance_info._subnet_cidr_block)
        instance_info._vpc_id = aws_network.vpc_id
        instance_info._gateway_id = aws_network.gateway_id
        instance_info._subnet_id = aws_network.subnet_id
        instance_info._route_table_id = aws_network._route_table_id
        instance_info._associate_id = aws_network._associate_id
        instance_info._group_id = aws_network._group_id
        instance_info._status = "created network"
        app_db.update_instance_info(instance_info)

    threading.Thread(target=run).start()
    #print("=========>{}".format(instance_info.to_dict()))
    #print("=========>{}".format(access_key_id))
    #print("=========>{}".format(secret_key))
    
    
    return index()

@app.route('/', methods=['GET'])
@app.route('/aws_info.update', methods=['GET'])
@app.route('/user_info.update', methods=['GET'])
@app.route('/inst.new', methods=['GET'])
@auth.login_required
def index():
    username = get_username_from_header()
    user: sv_db.User = app_db.get_user_info_from_email(username)
    instance_infos: List[InstanceInfo] = app_db.find_instance_info(user.id)
    print(f"===>{[i.to_dict() for i in instance_infos]} {user.id}")
    return render_template("index.html", template_folder=f"server/templates", username = username,
        aws_access_key_id = user.aws_access_key_id, aws_secret_key="",
        aws_region = user.aws_region, instance_infos=[i.to_dict() for i in instance_infos])

def setup():
    app_db.setup()

if __name__ == '__main__':
    setup()
    app.run(host="0.0.0.0",port=8080,threaded=True)




