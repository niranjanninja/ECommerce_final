from flask import Flask, redirect, url_for,render_template,request,flash,session
from flask_mail import Mail, Message
import bcrypt
from libs.UserDb import UserDb
from itsdangerous import URLSafeTimedSerializer,SignatureExpired
from login_parameter import Login
from configparser import ConfigParser
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import urllib.request
import os
import boto3
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from pathlib import Path
from datetime import timedelta

logger=logging.getLogger()
logger.setLevel(logging.INFO)
log_filename = datetime.now().strftime("logs/%d-%m-%Y.log")
handler=TimedRotatingFileHandler(filename = log_filename,when = "midnight", interval = 1 , backupCount = 7)
handler.setLevel(logging.INFO)
formatter=logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

file='/home/ubuntu/projectsql/login_page/libs/config.ini'
config=ConfigParser()
config.read(file)

app = Flask(__name__)
app.secret_key = config['Secret_key']['key']

# UPLOAD_FOLDER = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH']=1024*1024
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config.update(
	DEBUG=True,
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME =config['Mail_details']['mail_id'],
	MAIL_PASSWORD =config['Mail_details']['mail_pass']
	)
mailID= Mail(app)
serial=URLSafeTimedSerializer(config['Secret_key']['key'])

@app.route('/guest/<guest>')
def hello_guest(guest):
   return f'Hello welcome {guest}'

@app.route('/')
def index():
   return render_template("bootstrap_login.html")

@app.route('/signup')
def sign_up_index():
    country_code_list = []
    for code, regions in COUNTRY_CODE_TO_REGION_CODE.items():
        for region in regions:
            country_code_list.append((region, code))
            break
    country_code_list.sort()
    return render_template("bootstrap_sign_up.html", country_codes=country_code_list)


@app.route('/signuppage', methods=["GET", "POST"])
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
            print("Country codes:", country_code_list)
            return render_template("bootstrap_sign_up.html", country_codes=country_code_list)

        if request.method == "POST":
            name = request.form.get("name")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            number = request.form.get("number")
            country_code = request.form.get("country_code")
            mail = request.form.get("mail")
            full_number = country_code + number
            check = obj.get_all_details(name, password, confirm_password, full_number, mail)
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
                token = serial.dumps(mail, salt=config['URL_salt']['salt'])
                msg = Message('Confirm Mail', sender=config['Mail_details']['mail_id'], recipients=[mail])
                link = url_for('confirm_mail', token=token, _external=True)
                msg.html = render_template("welcome_mail.html",name=name,link=link)
                mailID.send(msg)
                mail_send = f"Confirmation mail has been sent to {mail}.\nThe link will expire in 5 minutes"
                return render_template("bootstrap_login.html", mail_send=mail_send,)
    except Exception as e:
        logger.error(f"error ->{e}")
        return f"Something went wrong"

@app.route('/confirm_mail/<token>')
def confirm_mail(token):
    obj=UserDb()
    try:
        email=serial.loads(token, salt=config['URL_salt']['salt'],max_age=600)
    except:
        return '<h1>Token Expired</h1>'
    name = obj.get_user_by_mail(email)
    msg = Message('Mail ID Confirmed', sender=config['Mail_details']['mail_id'], recipients=[email])
    msg.body = f"Hello {name}, your mail ID has been successfully confirmed."
    msg.html = render_template("confirm_mail.html", name=name)
    mailID.send(msg)
    result=obj.confirm_mail(email)
    return '<h1>You can now login to the page</h1>'


@app.route('/resetpassworddetails', methods=["POST"])
def reset_pass():
    try:
        obj=Login()
        if request.method == "POST":
            name=request.form.get("name")
            mail=request.form.get("mail")
            password=request.form.get("password")
            confirm_pass=request.form.get("confirm_pass")
            check_detail=obj.reset_password_details(name,mail,password,confirm_pass)
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
        return f"Something went wrong"


@app.route('/reset')
def show_reset():
    return render_template("bootstrap_forget_pass_details.html")

@app.route('/login', methods =["POST"])
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
                    session['username']=name
                    admin_check=obj.get_admin_detail(name)
                    if admin_check==True:
                        session.permanent=True
                        session['admin_logged']=True
                        session['username']=name
                        return redirect(url_for('hello_admin'))
                    else:
                        return redirect(url_for('home_page'))
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
        return f"Something went wrong"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/home')
def home_page():
    if not session.get('logged_in') and not session.get('admin_logged'):
        return redirect(url_for('index'))
    return render_template("homepage.html")


###############################################      ADMIN SIDE   ######################################################
@app.route('/admin')
def hello_admin():
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('index'))
        else:
            obj=UserDb()
            search=request.args.get('search')
            sort=request.args.get('sort')
            if search:
                search_num=obj.check_user_by_number(search)
                search_name=obj.check_user_by_name(search)
                search_mail=obj.check_user_by_mail(search)
                search_name_mail_num=search_name or search_mail or search_num
                page=request.args.get('page',1,type=int)
                per_page=13
                start=(page-1)*per_page
                end=start+per_page
                total_page=(len(search_name_mail_num)+per_page-1)//per_page
                item_on_page=search_name_mail_num[start:end]
                return render_template("table.html",length=len(search_name_mail_num),item_on_page=item_on_page,total_page=total_page,page=page)
            if sort:
                if sort=='username_asc':
                    username_asc=obj.sort_user_name_asc()
                    page=request.args.get('page',1,type=int)
                    per_page=13
                    start=(page -1) * per_page
                    end=start+per_page
                    total_page=(len(username_asc)+per_page-1) // per_page
                    item_on_page=username_asc[start:end]
                    return render_template("table.html",length=len(username_asc),item_on_page=item_on_page,total_page=total_page,page=page)
                elif sort=='username_desc':
                    username_desc=obj.sort_user_name_desc()
                    page=request.args.get('page',1,type=int)
                    per_page=13
                    start=(page -1) * per_page
                    end=start+per_page
                    total_page=(len(username_desc)+per_page-1) // per_page
                    item_on_page=username_desc[start:end]
                    return render_template("table.html",length=len(username_desc),item_on_page=item_on_page,total_page=total_page,page=page)
                elif sort=='usernumber_asc':
                    usernumber_asc=obj.sort_user_num_asc()
                    page=request.args.get('page',1,type=int)
                    per_page=13
                    start=(page -1) * per_page
                    end=start+per_page
                    total_page=(len(usernumber_asc)+per_page-1) // per_page
                    item_on_page=usernumber_asc[start:end]
                    return render_template("table.html",length=len(usernumber_asc),item_on_page=item_on_page,total_page=total_page,page=page)
                elif sort=='usernumber_desc':
                    usernumber_desc=obj.sort_user_num_desc()
                    page=request.args.get('page',1,type=int)
                    per_page=13
                    start=(page -1) * per_page
                    end=start+per_page
                    total_page=(len(usernumber_desc)+per_page-1) // per_page
                    item_on_page=usernumber_desc[start:end]
                    return render_template("table.html",length=len(usernumber_desc),item_on_page=item_on_page,total_page=total_page,page=page)
                elif sort=='mailid_asc':
                    mailid_asc=obj.sort_user_mail_asc()
                    page=request.args.get('page',1,type=int)
                    per_page=13
                    start=(page -1) * per_page
                    end=start+per_page
                    total_page=(len(mailid_asc)+per_page-1) // per_page
                    item_on_page=mailid_asc[start:end]
                    return render_template("table.html",length=len(mailid_asc),item_on_page=item_on_page,total_page=total_page,page=page)
                elif sort=='mailid_desc':
                    mailid_desc=obj.sort_user_mail_desc()
                    page=request.args.get('page',1,type=int)
                    per_page=13
                    start=(page -1) * per_page
                    end=start+per_page
                    total_page=(len(mailid_desc)+per_page-1) // per_page
                    item_on_page=mailid_desc[start:end]
                    return render_template("table.html",length=len(mailid_desc),item_on_page=item_on_page,total_page=total_page,page=page)
            else:
                store=obj.fetch()
                page=request.args.get('page',1,type=int)
                per_page=13
                start=(page-1)*per_page
                end=start+per_page
                total_page=(len(store)+per_page-1)//per_page
                item_on_page=store[start:end]
                return render_template("table.html",length=len(store),item_on_page=item_on_page,total_page=total_page,page=page)
    except Exception as e:
        logger.error(f"error -> {e}")
        return f"Something went wrong"

@app.route('/inventory_details')
def inventory_details():
    if not session.get('admin_logged'):
        return redirect(url_for('index'))
    else:
        return redirect(url_for('inventory'))

@app.route('/inventory',methods=["GET","POST"])
def inventory():
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('index'))
        else:
            obj=UserDb()
            obj3=Login()
            if request.method=="POST":
                product_id=request.form.get("product_id")
                check=obj3.inventory_delete(product_id)
                if "Item Deleted" in check:
                    flash("Item deleted","success")
                    logger.info("Item deleted")
                    return redirect(url_for('inventory'))
                if "NO" in check:
                    flash("Enter correct product ID","danger")
                    logger.warning("Enter correct product ID")
                    return redirect(url_for('inventory'))
            if request.method=="GET":
                search=request.args.get("search")
                sort=request.args.get("sort")
                if search:
                    if search.isdigit():
                        search_id=obj.inventory_by_id(search)
                        page=request.args.get('page',1,type=int)
                        per_page=4
                        start=(page -1) * per_page
                        end=start+per_page
                        total_page=(len(search_id)+per_page-1) // per_page
                        item_on_page=search_id[start:end]
                        item_on_page=list(item)
                        for item in item_on_page:
                            filename=item[5]
                            url=obj3.display_from_s3(filename)
                            item.append(url)
                        # print(item_on_page)
                        return render_template("inventory_page.html",length=len(search_id),item_on_page=item_on_page,total_page=total_page,page=page)
                    elif search:
                        search_name=obj.inventory_by_name(search)
                        page=request.args.get('page',1,type=int)
                        per_page=4
                        start=(page -1) * per_page
                        end=start+per_page
                        total_page=(len(search_name)+per_page-1) // per_page
                        item_on_page=search_name[start:end]
                        item_on_page=list(item)
                        for item in item_on_page:
                            filename=item[5]
                            url=obj3.display_from_s3(filename)
                            item.append(url)
                        # print(item_on_page)
                        return render_template("inventory_page.html",length=len(search_name),item_on_page=item_on_page,total_page=total_page,page=page)
                if sort:
                    if sort=='id_asc':
                        id_asc=obj.sort_inventory_id_asc()
                        page=request.args.get('page',1,type=int)
                        per_page=4
                        start=(page -1) * per_page
                        end=start+per_page
                        total_page=(len(id_asc)+per_page-1) // per_page
                        item_on_page=id_asc[start:end]
                        item_on_page=list(item)
                        for item in item_on_page:
                            filename=item[5]
                            url=obj3.display_from_s3(filename)
                            item.append(url)
                        # print(item_on_page)
                        return render_template("inventory_page.html",length=len(id_asc),item_on_page=item_on_page,total_page=total_page,page=page)
                    elif sort=='id_desc':
                        id_desc=obj.sort_inventory_id_desc()
                        page=request.args.get('page',1,type=int)
                        per_page=4
                        start=(page -1) * per_page
                        end=start+per_page
                        total_page=(len(id_desc)+per_page-1) // per_page
                        item_on_page=id_desc[start:end]
                        item_on_page=list(item)
                        for item in item_on_page:
                            filename=item[5]
                            url=obj3.display_from_s3(filename)
                            item.append(url)
                        # print(item_on_page)
                        return render_template("inventory_page.html",length=len(id_desc),item_on_page=item_on_page,total_page=total_page,page=page)
                    elif sort=='name_asc':
                        name_asc=obj.sort_inventory_name_asc()
                        page=request.args.get('page',1,type=int)
                        per_page=4
                        start=(page -1) * per_page
                        end=start+per_page
                        total_page=(len(name_asc)+per_page-1) // per_page
                        item_on_page=name_asc[start:end]
                        item_on_page=list(item)
                        for item in item_on_page:
                            filename=item[5]
                            url=obj3.display_from_s3(filename)
                            item.append(url)
                        # print(item_on_page)
                        return render_template("inventory_page.html",length=len(name_asc),item_on_page=item_on_page,total_page=total_page,page=page)
                    elif sort=='name_desc':
                        name_desc=obj.sort_inventory_name_desc()
                        page=request.args.get('page',1,type=int)
                        per_page=4
                        start=(page -1) * per_page
                        end=start+per_page
                        total_page=(len(name_desc)+per_page-1) // per_page
                        item_on_page=name_desc[start:end]
                        item_on_page=list(item)
                        for item in item_on_page:
                            filename=item[5]
                            url=obj3.display_from_s3(filename)
                            item.append(url)
                        # print(item_on_page)
                        return render_template("inventory_page.html",length=len(name_desc),item_on_page=item_on_page,total_page=total_page,page=page)
                    elif sort=='quantity_asc':
                        quantity_asc=obj.sort_inventory_quantity_asc()
                        page=request.args.get('page',1,type=int)
                        per_page=4
                        start=(page -1) * per_page
                        end=start+per_page
                        total_page=(len(quantity_asc)+per_page-1) // per_page
                        item_on_page=quantity_asc[start:end]
                        item_on_page=list(item)
                        for item in item_on_page:
                            filename=item[5]
                            url=obj3.display_from_s3(filename)
                            item.append(url)
                        # print(item_on_page)
                        return render_template("inventory_page.html",length=len(quantity_asc),item_on_page=item_on_page,total_page=total_page,page=page)
                    elif sort=='quantity_desc':
                        quantity_desc=obj.sort_inventory_quantity_desc()
                        page=request.args.get('page',1,type=int)
                        per_page=4
                        start=(page -1) * per_page
                        end=start+per_page
                        total_page=(len(quantity_desc)+per_page-1) // per_page
                        item_on_page=quantity_desc[start:end]
                        item_on_page=list(item)
                        for item in item_on_page:
                            filename=item[5]
                            url=obj3.display_from_s3(filename)
                            item.append(url)
                        # print(item_on_page)
                        return render_template("inventory_page.html",length=len(quantity_desc),item_on_page=item_on_page,total_page=total_page,page=page)
                    elif sort=='price_asc':
                        price_asc=obj.sort_inventory_price_asc()
                        page=request.args.get('page',1,type=int)
                        per_page=4
                        start=(page -1) * per_page
                        end=start+per_page
                        total_page=(len(price_asc)+per_page-1) // per_page
                        item_on_page=price_asc[start:end]
                        item_on_page=list(item)
                        for item in item_on_page:
                            filename=item[5]
                            url=obj3.display_from_s3(filename)
                            item.append(url)
                        # print(item_on_page)
                        return render_template("inventory_page.html",length=len(price_asc),item_on_page=item_on_page,total_page=total_page,page=page)
                    elif sort=='price_desc':
                        price_desc=obj.sort_inventory_price_desc()
                        page=request.args.get('page',1,type=int)
                        per_page=4
                        start=(page -1) * per_page
                        end=start+per_page
                        total_page=(len(price_desc)+per_page-1) // per_page
                        item_on_page=price_desc[start:end]
                        item_on_page=list(item)
                        for item in item_on_page:
                            filename=item[5]
                            url=obj3.display_from_s3(filename)
                            item.append(url)
                        # print(item_on_page)
                        return render_template("inventory_page.html",length=len(price_desc),item_on_page=item_on_page,total_page=total_page,page=page)
                else:
                    store=obj.inventory_show()
                    page=request.args.get('page',1,type=int)
                    per_page=4
                    start=(page -1) * per_page
                    end=start+per_page
                    total_page=(len(store)+per_page-1) // per_page
                    item_on_page=store[start:end]
                    item_on_page=list(item)
                    for item in item_on_page:
                        filename=item[5]
                        url=obj3.display_from_s3(filename)
                        item.append(url)
                    # print(item_on_page)
                    return render_template("inventory_page.html",length=len(store),item_on_page=item_on_page,total_page=total_page,page=page)
    except Exception as e:
        logger.error(f"error -> {e}")
        return f"Something went wrong {e}"

@app.route('/inven_add')
def inven_add():
    if not session.get('admin_logged'):
        return redirect(url_for('index'))
    else:
        return render_template("inventory_add.html")

@app.route('/inventory_add',methods=["GET","POST"])
def inventory_add():
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('index'))
        else:
            obj=UserDb()
            obj2=Login()
            if request.method=="POST":
                product_name=request.form.get("product_name")
                description=request.form.get("description")
                quantity=request.form.get("quantity")
                price=request.form.get("price")
                product_id=obj.inventory_add(product_name,description,quantity,price)
                # check=obj2.inventory_check_add(product_id)
                # if "Exist" in check:
                    # error="Product ID already Exist"
                    # return render_template("inventory_add.html",error=error)
                # if "NO" in check:
                if 'file' not in request.files:
                    flash('No file part')
                    logger.warning("No file part")
                    return redirect(url_for('inven_add'))
                file = request.files['file']
                if file.filename == '':
                    flash('No image selected for uploading')
                    logger.warning("No image selected for uploading")
                    return redirect(url_for('inven_add'))
                if file and allowed_file(file.filename):
                    # # Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
                    # filename = f"images/product_id{product_id}.jpg"
                    filename=obj2.bucket_save_image(file,product_id)
                    # s3 = boto3.resource("s3")
                    # bucket_name="webpage.image.upload"
                    # s3.Bucket(bucket_name).upload_fileobj(file,filename)
                    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    # filename=obj2.local_save_image(file,product_id)
                    store=obj.add_image_filename(product_id,filename)
                    flash("New Item Added","success")
                    logger.info("New Item Added")
                    return redirect(url_for('inventory'))
                    img_error="Allowed image types are - png, jpg, jpeg, gif"
                    logger.warning("Allowed image types are - png, jpg, jpeg, gif")
                    return render_template("inventory_add.html",img_error=img_error)
    except RequestEntityTooLarge:
        flash("File too large. Max size is 1MB.", "danger")
        logger.error("File too large. Max size is 1MB.")
        return redirect(url_for('inven_add'))
    except Exception as e:
        flash(f"Enter correct details","danger")
        logger.error(f"error -> {e}")
        return redirect(url_for('inven_add'))

@app.route('/edit_inventory/<product_id>')
def edit_inventory(product_id):
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('index'))
        else:
            obj = UserDb()
            result = obj.product_id_check(product_id)
            if result:
                return render_template("inventory_edit.html",product_id=result[0],product_name=result[1],description=result[2],quantity=result[3],price=result[4],image=result[5])
            return render_template("inventory_edit.html",image=image)
    except Exception as e:
        logger.error(f"error -> {e}")
        # return f"Something went wrong"
        return redirect(url_for('inventory'))

@app.route('/delete_item/<product_id>')
def delete_item(product_id):
    if not session.get('admin_logged'):
        return redirect(url_for('index'))
    else:
        obj=UserDb()
        # filename = f"product_id{product_id}.jpg"
        # path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # if os.path.exists(path):
            # try:
                # os.remove(path)
                # result=obj.inventory_delete(product_id)
                # return redirect(url_for('inventory'))
            # except Exception:
                # return f"Something Went Wrong"
        # else:
        result=obj.inventory_delete(product_id)
        return redirect(url_for('inventory'))


@app.route('/view_item/<product_id>')
def view_item(product_id):
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('index'))
        else:
            obj = UserDb()
            result = obj.product_id_check(product_id)
            if result:
                return render_template("view_products.html",product_id=result[0],product_name=result[1],description=result[2],quantity=result[3],price=result[4],image=result[5])
            return render_template("view_products.html",image=image)
    except Exception as e:
        logger.error(f"error -> {e}")
        return redirect(url_for('inventory'))

@app.route('/inventory_edit', methods=["POST"])
def inventory_edit():
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('index'))
        else:
            obj = UserDb()
            obj2 = Login()
            product_id = request.form.get("product_id")
            name = request.form.get("product_name")
            description = request.form.get("description")
            quantity = request.form.get("quantity")
            price = request.form.get("price")
            check = obj2.inventory_edit(product_id)
            if "NO" in check:
                error = "Enter a valid Product ID"
                logger.warning("Enter a valid Product ID")
                return render_template("inventory_edit.html", error=error)
            elif "Exist" in check:
                if name:
                    obj.inventory_edit_name(product_id, name)
                if description:
                    obj.inventory_edit_description(product_id, description)
                if quantity:
                    obj.inventory_edit_quantity(product_id, quantity)
                if price:
                    obj.inventory_edit_price(product_id, price)
                file = request.files.get('file')
                if file and allowed_file(file.filename):
                    # Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
                    filename = f"images/product_id{product_id}.jpg"
                    s3 = boto3.resource("s3")
                    bucket_name="webpage.image.upload"
                    s3.Bucket(bucket_name).upload_fileobj(file,filename)
                    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    obj.inventory_edit_image(product_id, filename)
                elif file and file.filename != '' and not allowed_file(file.filename):
                    flash("Allowed image types are - png, jpg, jpeg, gif","danger")
                    logger.warning("Allowed image types are - png, jpg, jpeg, gif")
                    return redirect(url_for('edit_inventory',product_id=product_id))
                flash("Updated", "success")
                logger.info("Updated")
                return redirect(url_for('inventory'))
    except Exception as e:
        flash("Check and enter correct details","danger")
        logger.error(f"error -> {e}")
        return redirect(url_for('edit_inventory',product_id=product_id))

if __name__ == '__main__':
   app.run(host='0.0.0.0',port=5000)


