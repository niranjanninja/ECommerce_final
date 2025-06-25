from flask import Flask, redirect, url_for,render_template,request,flash,session
from flask_mail import Mail, Message
import bcrypt
from libs.UserDb import UserDb
from itsdangerous import URLSafeTimedSerializer,SignatureExpired
from login_parameter import Login
from configparser import ConfigParser
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE
file='/home/niranjan/projectsql/login_page/libs/config.ini'
config=ConfigParser()
config.read(file)

app = Flask(__name__)
app.secret_key = config['Secret_key']['key']

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
# @app.route('/<username>')
# def hello_world(username):
#    return f"Hello <head>Niranjan </head> {username}"

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
            return render_template("bootstrap_sign_up.html", user_error=user_error, country_codes=country_code_list)
        if "Password does not match" in check:
            pass_error = 'Password does not match'
            return render_template("bootstrap_sign_up.html", pass_error=pass_error, country_codes=country_code_list)
        if "Enter valid password" in check:
            pass_error2 = 'Enter valid password. Password must have minimum 10 characters.'
            return render_template("bootstrap_sign_up.html", pass_error2=pass_error2, country_codes=country_code_list)
        if "Enter valid number" in check:
            num_error = 'Enter a valid phone number'
            return render_template("bootstrap_sign_up.html", num_error=num_error, country_codes=country_code_list)
        if "Number already exist" in check:
            num_error2 = 'Phone number already exists'
            return render_template("bootstrap_sign_up.html", num_error2=num_error2, country_codes=country_code_list)
        if "Enter valid Mail ID" in check:
            mail_error = "Enter valid Mail ID"
            return render_template("bootstrap_sign_up.html", mail_error=mail_error, country_codes=country_code_list)
        if "Mail id exist" in check:
            mail_error2 = "Mail id already exists"
            return render_template("bootstrap_sign_up.html", mail_error2=mail_error2, country_codes=country_code_list)
        if "Inserted into DB" in check:
            token = serial.dumps(mail, salt=config['URL_salt']['salt'])
            msg = Message('Confirm Mail', sender=config['Mail_details']['mail_id'], recipients=[mail])
            link = url_for('confirm_mail', token=token, _external=True)
            msg.body = f"Hi {name}\nClick on the link to confirm your Mail ID {format(link)}"
            # msg.html = "<html><body><p>Hi {name}\nClick on the link to confirm your Mail ID {format(link)}</p></body></html>"
            mailID.send(msg)
            mail_send = f"Confirmation mail has been sent to {mail}.\nThe link will expire in 5 minutes"
            return render_template("bootstrap_login.html", mail_send=mail_send,)

@app.route('/confirm_mail/<token>')
def confirm_mail(token):
    obj=UserDb()
    try:
        email=serial.loads(token, salt=config['URL_salt']['salt'],max_age=600)
    except:
        return '<h1>Token Expired</h1>'
    result=obj.confirm_mail(email)
    return '<h1>Mail ID Verified</h1><p>You can now login to the page</p>'


@app.route('/resetpassworddetails', methods=["POST"])
def reset_pass():
    obj=Login()
    if request.method == "POST":
        name=request.form.get("name")
        mail=request.form.get("mail")
        password=request.form.get("password")
        confirm_pass=request.form.get("confirm_pass")
        check_detail=obj.reset_password_details(name,mail,password,confirm_pass)
        if "Username/Mail ID does not exist" in check_detail:
            user_error='Username/Mail ID does not exist'
            return render_template("bootstrap_forget_pass_details.html",user_error=user_error)
        if "Enter valid password" in check_detail:
            pass_error2='Enter valid password. Password must have minimum 10 characters'
            return render_template("bootstrap_forget_pass_details.html",pass_error2=pass_error2)
        if "Password does not match" in check_detail:
            pass_error='Password does not match' 
            return render_template("bootstrap_forget_pass_details.html",pass_error=pass_error)
        if "Old password should not be the new password" in check_detail:
            pass_error3='Old password should not be the new password'
            return render_template("bootstrap_forget_pass_details.html",pass_error3=pass_error3)
        if "Updated" in check_detail:
            pass_update='Password Updated'
            # return redirect(url_for('index'))
            return render_template("bootstrap_login.html",pass_update=pass_update)
        # else:
        #     return redirect(url_for('show_reset'))


@app.route('/reset')
def show_reset():
    return render_template("bootstrap_forget_pass_details.html")

@app.route('/login', methods =["POST"])
def result_store():
    obj=UserDb()
    if request.method == "POST":
        name= request.form.get("name")
        password= request.form.get("password")
        check_name=obj.get_name(name)
        if check_name:
            check_hash=obj.get_user_by_name(name)
            if bcrypt.checkpw(password.encode('utf-8'),check_hash.encode('utf-8')):
                return redirect(url_for('home_page'))
            else:
                error='Invalid username or password'
                # return redirect(url_for('index'))
                return render_template("bootstrap_login.html",error1=error)
                
        else:
            error2='Invalid username or password'
            # return redirect(url_for('index'))
            return render_template("bootstrap_login.html",error2=error2)

@app.route('/home')
def home_page():
    return render_template("homepage.html")

@app.route('/admin')
def hello_admin():
    obj=UserDb()
    store=obj.fetch()
    return render_template("table.html", details=store,length=len(store))

@app.route('/inventory_details')
def inventory_details():
    return redirect(url_for('inventory'))

@app.route('/inventory',methods=["GET","POST"])
def inventory():
    obj=UserDb()
    obj2=Login()
    if request.method=="POST":
        product_id=request.form.get("product_id")
        check=obj2.inventory_delete(product_id)
        if "Item Deleted" in check:
            flash("Item deleted","success")
            return redirect(url_for('inventory'))
        if "NO" in check:
            flash("Enter correct product ID","danger")
            return redirect(url_for('inventory'))
    if request.method=="GET":
        store=obj.inventory_show()
        return render_template("inventory_page.html",details=store,length=len(store))

@app.route('/inven_add')
def inven_add():
    return render_template("inventory_add.html")

@app.route('/inventory_add',methods=["GET","POST"])
def inventory_add():
    obj=UserDb()
    obj2=Login()
    if request.method=="POST":
        product_id=request.form.get("product_id")
        product_name=request.form.get("product_name")
        description=request.form.get("description")
        quantity=request.form.get("quantity")
        price=request.form.get("price")
        check=obj2.inventory_check_add(product_id)
        if "Exist" in check:
            error="Product ID already Exist"
            return render_template("inventory_add.html",error=error)
        if "NO" in check:
            store=obj.inventory_add(product_id,product_name,description,quantity,price)
            flash("New Item Added","success")
            return redirect(url_for('inventory'))

@app.route('/edit_inventory/<product_id>')
def edit_inventory(product_id):
    obj = UserDb()
    result = obj.product_id_check(product_id)
    print("Product fetched:", result) 
    if result:
        return render_template("inventory_edit.html",product_id=result[0],name=result[1],description=result[2],quantity=result[3],price=result[4])
    return render_template("inventory_edit.html")

@app.route('/inventory_edit', methods=["POST"])
def inventory_edit():
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

        flash("Updated", "success")
        return redirect(url_for('inventory'))

            # column = request.form.get("column")
            # new_value = request.form.get("new_value")
            # if column and new_value:
            #     if column == "product_name":
            #         obj.inventory_edit_name(product_id, new_value)
            #         flash("Updated","success")
            #         return redirect(url_for('inventory'))
            #     elif column == "description":
            #         obj.inventory_edit_description(product_id, new_value)
            #         flash("Updated","success")
            #         return redirect(url_for('inventory'))
            #     elif column == "quantity":
            #         obj.inventory_edit_quantity(product_id, new_value)
            #         flash("Updated","success")
            #         return redirect(url_for('inventory'))
            #     elif column == "price":
            #         obj.inventory_edit_price(product_id, new_value)
            #         flash("Updated","success")
            #         return redirect(url_for('inventory'))

            
@app.route('/user/<name>')
def hello_user(name):
    if name =='admin':
        print(url_for('hello_admin'))
        return redirect(url_for('hello_admin'))
    else:
        return redirect(url_for('hello_guest'))
if __name__ == '__main__':
   app.run(debug = True)


