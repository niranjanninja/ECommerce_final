from flask import Flask, redirect, url_for,render_template,request,flash,session,Blueprint
from loggers import Loggers 
from configparser import ConfigParser
import logging
from login_blueprint import login
from homepage_blurprint import home
from inventory_blueprint import inventory
from admin_blueprint import admin

Loggers.loggers()
logger = logging.getLogger()

file='/home/ubuntu/projectsql/login_page/libs/config.ini'
config=ConfigParser()
config.read(file)

app = Flask(__name__)
app.register_blueprint(login)
app.register_blueprint(home)
app.register_blueprint(inventory)
app.register_blueprint(admin)
app.secret_key = config['Secret_key']['key']

if __name__ == '__main__':
   app.run(host='0.0.0.0',port=5000)

