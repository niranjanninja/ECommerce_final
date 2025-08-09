from flask import Flask, redirect, url_for,render_template,request,flash,session,Blueprint
# import bcrypt
from libs.UserDb import UserDb
# from itsdangerous import URLSafeTimedSerializer,SignatureExpired
from login_parameter import Login,Image_upload
from loggers import Loggers
from configparser import ConfigParser
import logging
# import urllib.request
# import os
# import boto3
# from werkzeug.utils import secure_filename
# from werkzeug.exceptions import RequestEntityTooLarge
# from pathlib import Path
# from datetime import timedelta
# from login_blueprint import login

app = Flask(__name__)

Loggers.loggers()
logger = logging.getLogger()

home=Blueprint("home",__name__,template_folder="templates")

@home.route('/home')
def home_page():
    try:
        obj=UserDb()
        obj2=Image_upload()
        obj3=Login()
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        name=session.get('name')
        image=obj.random_from_inventory()
        url_list=[]
        for i in image:
            url_list2=[]
            url=obj2.display_single_from_s3(i[0])
            url_list2.append(url)
            url_list2.append(i[1])
            url_list2.append(i[2])
            url_list2.append(i[3])
            url_list2.append(i[4])
            url_list.append(url_list2)
        search=request.args.get('search')
        page=request.args.get('page',1,type=int)
        if search:
            search_url_list=[]
            search=obj3.homepage_search(search,page)
            for i in search[1]:
                search_url_list2=[]
                search_url=obj2.display_single_from_s3(i[0])
                search_url_list2.append(search_url)
                search_url_list2.append(i[1])
                search_url_list2.append(i[2])
                search_url_list2.append(i[3])
                search_url_list2.append(i[4])
                search_url_list.append(search_url_list2)
            return render_template("homepage.html",name=name,length=len(search_url_list),url_list=search_url_list,total_page=search[2],page=page)
        else:
            page=request.args.get('page',1,type=int)
            per_page=6
            start=(page -1) * per_page
            end=start+per_page
            total_page=(len(url_list)+per_page-1) // per_page
            item_on_page=url_list[start:end]
            return render_template("homepage.html",name=name,url_list=item_on_page,length=len(url_list),total_page=total_page,page=page)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return redirect(url_for('home.home_page'))

@home.route('/cpu_items',methods=["GET","POST"])
def cpu_items():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        name=session.get('name')
        return render_template("cpu_page.html",name=name)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/headphone_items',methods=["GET","POST"])
def headphone_items():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        name=session.get('name')
        return render_template("headphone_page.html",name=name)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/keyboard_items',methods=["GET","POST"])
def keyboard_items():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        name=session.get('name')
        return render_template("keyboard_page.html",name=name)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/monitor_items',methods=["GET","POST"])
def monitor_items():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        name=session.get('name')
        return render_template("monitor_page.html",name=name)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/mouse_items',methods=["GET","POST"])
def mouse_items():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        name=session.get('name')
        return render_template("mouse_page.html",name=name)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/speaker_items',methods=["GET","POST"])
def speaker_items():
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        name=session.get('name')
        return render_template("speaker_page.html",name=name)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))

@home.route('/item/<product_id>')
def show_item_user(product_id):
    try:
        if not session.get('logged_in') and not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            obj=UserDb()
            obj2=Image_upload()
            store=obj.fetch_product_user(product_id)
            for i in store:
                url=obj2.display_from_s3(i[5])
            return render_template("show_product_user.html",name=name,url=url,product_id=product_id,product_brand=store[0][0],product_name=store[0][1],description=store[0][2],features=store[0][3],price=store[0][4])
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"error ->{e}"
        # return redirect(url_for('home_page'))


