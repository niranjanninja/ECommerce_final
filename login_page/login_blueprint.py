from flask import Flask, redirect, url_for,render_template,request,flash,session,Blueprint
from flask_mail import Mail, Message
import bcrypt
from libs.UserDb import UserDb
from itsdangerous import URLSafeTimedSerializer,SignatureExpired
from configparser import ConfigParser
from login_parameter import Login
from loggers import Loggers
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import urllib.request
from pathlib import Path
from datetime import timedelta
from homepage_blurprint import home

Loggers.loggers()
logger = logging.getLogger()
app = Flask(__name__)
app.register_blueprint(home)

file='/home/ubuntu/projectsql/login_page/libs/config.ini'
config=ConfigParser()
config.read(file)


app.config.update(
        DEBUG=True,
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_USERNAME =config['Mail_details']['mail_id'],
        MAIL_PASSWORD =config['Mail_details']['mail_pass']
        )
mail= Mail(app)
serial=URLSafeTimedSerializer(config['Secret_key']['key'])

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

login=Blueprint("login",__name__,template_folder="templates")

@login.route('/')
def index():
   return render_template("bootstrap_login.html")

@login.route('/signup')
def sign_up_index():
    country_code_list = []
    for code, regions in COUNTRY_CODE_TO_REGION_CODE.items():
        for region in regions:
            country_code_list.append((region, code))
            break
    country_code_list.sort()
    return render_template("bootstrap_sign_up.html", country_codes=country_code_list)

@login.route('/signuppage', methods=["GET", "POST"])
def sign_up_page_index():
    try:
        country_code_list = []
        for code, regions in COUNTRY_CODE_TO_REGION_CODE.items():
            for region in regions:
                country_code_list.append((region, code))
                break
        country_code_list.sort()
        obj = Login()
        if request.method == "GET":
            return render_template("bootstrap_sign_up.html", country_codes=country_code_list)

        if request.method == "POST":
            name = request.form.get("name")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            number = request.form.get("number")
            country_code = request.form.get("country_code")
            user_mail = request.form.get("mail")
            print(f'user mail print ->{mail}')
            full_number = country_code + number
            check = obj.get_all_details(name, password, confirm_password, full_number, user_mail)
            if "Username already exist" in check:
                user_error = 'Username already exists. Try using a different username.'
                logger.warning("Username already exists. Try using a different username.")
                return render_template("bootstrap_sign_up.html", user_error=user_error, country_codes=country_code_list)
            if "Password does not match" in check:
                pass_error = 'Password does not match'
                logger.warning("Password does not match")
                return render_template("bootstrap_sign_up.html", pass_error=pass_error, country_codes=country_code_list)
            if "Enter valid password" in check:
                pass_error2 = 'Enter valid password. Password must have minimum 10 characters.'
                logger.warning("Enter valid password. Password must have minimum 10 characters.")
                return render_template("bootstrap_sign_up.html", pass_error2=pass_error2, country_codes=country_code_list)
            if "Enter valid number" in check:
                num_error = 'Enter a valid phone number'
                logger.warning("Enter a valid phone number")
                return render_template("bootstrap_sign_up.html", num_error=num_error, country_codes=country_code_list)
            if "Number already exist" in check:
                num_error2 = 'Phone number already exists'
                logger.warning("Phone number already exists")
                return render_template("bootstrap_sign_up.html", num_error2=num_error2, country_codes=country_code_list)
            if "Enter valid Mail ID" in check:
                mail_error = "Enter valid Mail ID"
                logger.warning("Enter valid Mail ID")
                return render_template("bootstrap_sign_up.html", mail_error=mail_error, country_codes=country_code_list)
            if "Mail id exist" in check:
                mail_error2 = "Mail id already exists"
                logger.warning("Mail id already exists")
                return render_template("bootstrap_sign_up.html", mail_error2=mail_error2, country_codes=country_code_list)
            if "Inserted into DB" in check:
                token = serial.dumps(user_mail, salt=config['URL_salt']['salt'])
                msg = Message('Confirm Mail', sender=config['Mail_details']['mail_id'], recipients=[user_mail])
                link = url_for('login.confirm_mail', token=token, _external=True)
                msg.html = render_template("welcome_mail.html",name=name,link=link)
                print(f"message.html -> {msg.html}")
                print(f"mail -> {mail}")
                mail.send(msg)
                mail_send = f"Confirmation mail has been sent to {user_mail}.\nThe link will expire in 5 minutes"
                return render_template("bootstrap_login.html", mail_send=mail_send,)
    except Exception as e:
        logger.error(f"error ->{e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"Something went wrong"

@login.route('/confirm_mail/<token>')
def confirm_mail(token):
    try:
        obj=UserDb() 
        email=serial.loads(token, salt=config['URL_salt']['salt'],max_age=600)
    except:
        return '<h1>Token Expired</h1>'
    name = obj.get_user_by_mail(email)
    msg = Message('Mail ID Confirmed', sender=config['Mail_details']['mail_id'], recipients=[email])
    msg.body = f"Hello {name}, your mail ID has been successfully confirmed."
    msg.html = render_template("confirm_mail.html", name=name)
    mail.send(msg)
    result=obj.confirm_mail(email)
    return '<h1>You can now login to the page</h1>'

@login.route('/resetpassworddetails', methods=["POST"])
def reset_pass():
    try:
        obj=Login()
        if request.method == "POST":
            name=request.form.get("name")
            user_mail=request.form.get("mail")
            password=request.form.get("password")
            confirm_pass=request.form.get("confirm_pass")
            check_detail=obj.reset_password_details(name,user_mail,password,confirm_pass)
            if "Username/Mail ID does not exist" in check_detail:
                user_error='Username/Mail ID does not exist'
                logger.warning("Username/Mail ID does not exist")
                return render_template("bootstrap_forget_pass_details.html",user_error=user_error)
            if "Enter valid password" in check_detail:
                pass_error2='Enter valid password. Password must have minimum 10 characters'
                logger.warning("Enter valid password. Password must have minimum 10 characters")
                return render_template("bootstrap_forget_pass_details.html",pass_error2=pass_error2)
            if "Password does not match" in check_detail:
                pass_error='Password does not match'
                logger.warning("Password does not match")
                return render_template("bootstrap_forget_pass_details.html",pass_error=pass_error)
            if "Old password should not be the new password" in check_detail:
                pass_error3='Old password should not be the new password'
                logger.warning("Old password should not be the new password")
                return render_template("bootstrap_forget_pass_details.html",pass_error3=pass_error3)
            if "Updated" in check_detail:
                pass_update='Password Updated'
                logger.info("Password Updated")
                return render_template("bootstrap_login.html",pass_update=pass_update)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"Something went wrong"

@login.route('/reset')
def show_reset():
    return render_template("bootstrap_forget_pass_details.html")

@login.route('/login', methods =["POST"])
def result_store():
    try:
        obj=UserDb()
        if request.method == "POST":
            name= request.form.get("name")
            password= request.form.get("password")
            check_name=obj.get_name(name)
            if check_name:
                check_hash=obj.get_user_by_name(name)
                if bcrypt.checkpw(password.encode('utf-8'),check_hash.encode('utf-8')):
                    session.permanent=True
                    session['logged_in']=True
                    session['name']=name
                    admin_check=obj.get_admin_detail(name)
                    if admin_check==True:
                        session.permanent=True
                        session['admin_logged']=True
                        session['name']=name
                        return redirect(url_for('admin.hello_admin',name=name))
                    else:
                        return redirect(url_for('home.home_page',name=name))
                else:
                    error='Invalid username or password'
                    logger.warning("Invalid username or password")
                    return render_template("bootstrap_login.html",error1=error)
            else:
                error2='Invalid username or password'
                logger.warning("Invalid username or password")
                return render_template("bootstrap_login.html",error2=error2)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"Something went wrong"

@login.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login.index'))
