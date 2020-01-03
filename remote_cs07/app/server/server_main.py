from typing import Dict, List
import os
import re
from flask import Flask, Response, request, render_template
from flask_httpauth import HTTPDigestAuth
import flask
import threading
import dataset
import sqlalchemy
#
import boto3
import sys, getopt
from boto3_type_annotations import ec2
from botocore.exceptions import ClientError
import logging
#
import server.database as sv_db
from server.instance_info import InstanceInfo
from aws.network import AWSNetwork, create_network ,delete_network
from aws.instance import AWSInstance, create_instance, delete_instance


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
def _get_password_from_db(email):
    user: sv_db.User = app_db.get_user_info_from_email(email)
    if user != None:
        return user.password
    return None

@app.route('/app.init', methods=['POST'])
def _init_app():
    try:
        password = request.form.get('password', "")
        email = request.form.get('email', "")
        if app_db.init_app(email, password):
            return index()
        else:
            return "Already Initialized"
    except:
        logging.exception("Failed at /app.init", exc_info=True)
        return index("Failed at /app.init")        

@app.route('/app.logout', methods=['POST'])
def _logout_app():
    resp = flask.make_response("<a href='/'>back to index</a>")
    resp.status_code = 401
    return resp

@app.route('/user_info.update', methods=['POST'])
@auth.login_required
def _update_user_info():
    try:
        next_password = request.form.get('password', "")
        if len(next_password) < 8:
            logging.exception("Password must be at least 8 characters long", exc_info=True)
            return index("Password must be at least 8 characters long")    
        username = get_username_from_header()
        user: sv_db.User = app_db.get_user_info_from_email(username)
        user._password = next_password
        app_db.update_user(user)
        return index()
    except:
        logging.exception("Failed at /user_info.update", exc_info=True)
        return index("Failed at /user_info.update")

@app.route('/aws_info.update', methods=['POST'])
@auth.login_required
def _update_aws_info():
    try:
        username = get_username_from_header()
        user: sv_db.User = app_db.get_user_info_from_email(username)
        user._aws_access_key_id = request.form.get('aws_access_key_id', "")
        user._aws_secret_key = request.form.get('aws_secret_key', "")
        user._aws_region = request.form.get('aws_region', "")
        app_db.update_user(user)
        return index()
    except:
        logging.exception("Failed at /aws_info.update", exc_info=True)
        return index("Failed at /aws_info.update")


@app.route('/inst.get_pem', methods=['POST'])
@auth.login_required
def _get_pem():
    try:
        username = get_username_from_header()
        user: sv_db.User = app_db.get_user_info_from_email(username)
        instance_infos: List[InstanceInfo] = app_db.find_instance_info(user.id)
        name = request.form.get('name', "")
        pems = [info.pem for info in instance_infos if info.name == name]
        if len(pems) <= 0:
            return index("Not Found Pem")
        #print(f"==>{pems[0]}")
        return flask.Response(response=pems[0], status=200, mimetype="text/plain")
    except:
        logging.exception("Failed at /inst.get_pem", exc_info=True)
        return index("Failed at /inst.get_pem")

@app.route('/inst.new', methods=['POST'])
@auth.login_required
def _new_instance():
    try:
        username = get_username_from_header()
        user: sv_db.User = app_db.get_user_info_from_email(username)

        #
        # CHECK
        if "" == request.form.get('name', ""):
            return index(f"Require Name {request.form.get('name', '')}") 

        if request.form.get('name', "") in [i.name for i in app_db.find_instance_info(user.id)]:
            return index(f"Already Exist {request.form.get('name', '')}")

        if user.aws_access_key_id.strip() == "":
            return index("Reuqire aws_access_key_id ")

        if user.aws_secret_key.strip() == "":
            return index("Reuqire aws_secret_key. ")

        if user.aws_region.strip() == "":
            return index("Reuqire aws_region. ")

        #
        # prepare instance info
        instance_info: InstanceInfo = InstanceInfo()
        instance_info._name = request.form.get('name', "")
        instance_info._vpc_cidr_block = request.form.get('vpc_cidr_block', "")
        instance_info._subnet_cidr_block = request.form.get('subnet_cidr_block', "")
        instance_info._instance_type = request.form.get('instance_type', "")
        instance_info._image_type = request.form.get('image_type', "")
        instance_info._status = "before running"
        instance_info._user_id = user.id
        app_db.update_instance_info(instance_info)


        try:
            ec2_client:ec2.Client = boto3.client("ec2", region_name=user.aws_region.strip(), 
            aws_access_key_id=user.aws_access_key_id.strip(),aws_secret_access_key=user.aws_secret_key.strip())
        except:
            logging.exception("Failed to create ec2 client", exc_info=True)
            return index("Failed to create ec2 client ")

        aws_network: AWSNetwork = AWSNetwork(ec2_client, project_name=instance_info._name, 
            ports=[22,8443,8080], vpc_cidr_block=instance_info._vpc_cidr_block, subnet_cidr_block=instance_info._subnet_cidr_block)

        aws_instance: AWSInstance = AWSInstance(ec2_client, project_name=instance_info._name, instance_type=instance_info._instance_type, image_id=instance_info.image_type)
        def run():
            try:
                # create network
                create_network(aws_network)
                instance_info._vpc_id = aws_network.vpc_id
                instance_info._gateway_id = aws_network.gateway_id
                instance_info._subnet_id = aws_network.subnet_id
                instance_info._route_table_id = aws_network._route_table_id
                instance_info._associate_id = aws_network._associate_id
                instance_info._group_id = aws_network._group_id
                instance_info._status = "created network"
                app_db.update_instance_info(instance_info)
                # create instance
                create_instance(aws_instance, aws_network)
                instance_info._instance_id = aws_instance.instance_id
                instance_info._status = "created instance"
                instance_info._pem = aws_instance.pem_data
                app_db.update_instance_info(instance_info)
            except:
                logging.exception("Failed at /inst.new run()", exc_info=True)

        threading.Thread(target=run).start()
    except:
        logging.exception("Failed at /inst.new", exc_info=True)

    return index()


@app.route('/inst.delete', methods=['POST'])
@auth.login_required
def _delete_instance():
    try:
        username = get_username_from_header()
        user: sv_db.User = app_db.get_user_info_from_email(username)
        #
        # CHECK
        if "" == request.form.get('name', ""):
            return index(f"Require Name {request.form.get('name', '')}") 

        if user.aws_access_key_id.strip() == "":
            return index("Reuqire aws_access_key_id ")

        if user.aws_secret_key.strip() == "":
            return index("Reuqire aws_secret_key. ")

        if user.aws_region.strip() == "":
            return index("Reuqire aws_region. ")


        instance_info:InstanceInfo = InstanceInfo()
        instance_info._name = request.form.get('name', "")

        name =  request.form.get('name', "")
        if name == "":
            return index(f"Require Name {request.form.get('name', '')}") 

        targets = [i for i in app_db.find_instance_info(user.id) if i.name == name]
        if len(targets) == 0:
            return index(f"Not Found {request.form.get('name', '')}") 

        instance_info = targets[0]

        try:
            ec2_client:ec2.Client = boto3.client("ec2", region_name=user.aws_region.strip(), 
                aws_access_key_id=user.aws_access_key_id.strip(),aws_secret_access_key=user.aws_secret_key.strip())
        except:
            logging.exception("Failed to delete ec2 client", exc_info=True)
            return index("Failed to delete ec2 client ")

        aws_network: AWSNetwork = AWSNetwork(ec2_client, project_name=instance_info._name.strip(), 
            ports=[22,8443,8080], vpc_cidr_block=instance_info._vpc_cidr_block, subnet_cidr_block=instance_info._subnet_cidr_block)
        aws_instance: AWSInstance = AWSInstance(ec2_client, project_name=instance_info._name, instance_type=instance_info._instance_type, image_id=instance_info.image_type)

        def run():
            try:
                print("===> delete instance")
                delete_instance(aws_instance)
                instance_info._status = "deleting instance"
                app_db.update_instance_info(instance_info)
                print("===> wait ")
                aws_instance.wait_instance_is_terminated()
                instance_info._status = "deleted instance"
                app_db.update_instance_info(instance_info)

                print("===> delete network")
                delete_network(aws_network)
                print("===> delete instance info")
                app_db.delete_instance_info(targets[0].name)
                print("===> end")
            except:
                logging.exception("Failed at /inst.delete run()", exc_info=True)

        threading.Thread(target=run).start()
        return index()
    except:
        logging.exception("Failed at /inst.delete", exc_info=True)
        return index("Failed at /inst.delete")


@app.route('/init', methods=['GET'])
def _init():
    return render_template("init.html")

@app.route('/', methods=['GET'])
@app.route('/aws_info.update', methods=['GET'])
@app.route('/user_info.update', methods=['GET'])
@app.route('/inst.delete', methods=['GET'])
@app.route('/inst.new', methods=['GET'])
@app.route('/app.logout', methods=['GET'])
@auth.login_required
def index(error_message:str=""):
    try:
        username = get_username_from_header()
        user: sv_db.User = app_db.get_user_info_from_email(username)
        instance_infos: List[InstanceInfo] = app_db.find_instance_info(user.id)
        return render_template("index.html", username = username,
            aws_access_key_id = user.aws_access_key_id, aws_secret_key="",
            aws_region = user.aws_region, instance_infos=[i.to_dict() for i in instance_infos],
            error_message = error_message)
    except:
        logging.exception("Failed to create page", exc_info=True)
        return "Failed to create page"

def setup():
    app_db.setup()

if __name__ == '__main__':
    setup()
    app.run(host="0.0.0.0",port=8080,threaded=True)




