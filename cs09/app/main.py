from flask import Flask, request as fl_request, Request
from typing import Dict
import json
import dataset
# https://github.com/pudo/dataset
import logging

app =Flask(__name__)
logger = logging.getLogger("XXX")
logging.basicConfig(level=logging.DEBUG)

db:dataset.Database = dataset.connect('mysql://root:passwd@mysqld/app_db')

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/users")
def get_user_from_id():
    request:Request = fl_request
    input:Dict = request.args
    logger.debug("> input: {}".format(input))
    users_table:dataset.Table = db.get_table("users")
    user:Dict = users_table.find_one(id=int(input["id"]))
    return json.dumps(user)

app.run("0.0.0.0", port=8080)


# 
# apt-get install libmariadbclient-dev
# apt-get install python-mysqldb
# pip install mysqlclient
#