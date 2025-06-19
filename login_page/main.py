from flask import Flask, redirect, url_for,render_template,request,flash
# from flask_mail import Mail, Message
import bcrypt
from libs.UserDb import UserDb
from login_parameter import Login
app = Flask(__name__)

# @app.route('/<username>')
# def hello_world(username):
#    return f"Hello <head>Niranjan </head> {username}"

@app.route('/guest/<guest>')
def hello_guest(guest):
   return f'Hello welcome {guest}'

@app.route('/')
def index():
   return render_template("login.html")

@app.route('/signup')
def sign_up_index():
   return render_template("sign_up.html")

@app.route('/signuppage',methods=["POST"])
def sign_up_page_index():
    obj=Login()
    if request.method == "POST":
        name=request.form.get("name")
        password=request.form.get("password")
        confirm_password=request.form.get("confirm_password")
        number=request.form.get("number")
        mail=request.form.get("mail")
        check=obj.get_all_details(name,password,confirm_password,number,mail)
        if "Username already exist" in check:
            user_error='Username already exists'
            return render_template("sign_up.html",user_error=user_error)
        if "Password does not match" in check :
            pass_error='Password does not match'
            return render_template("sign_up.html",pass_error=pass_error)
        if "Enter valid password" in check:
            pass_error2='Enter valid password'
            return render_template("sign_up.html",pass_error2=pass_error2)
        if "Enter valid number" in check:
            num_error= 'Enter valid number'
            return render_template("sign_up.html",num_error=num_error)
        if "Number already exist" in check:
            num_error2='Number already exist'
            return render_template("sign_up.html",num_error2=num_error2)
        if "Enter valid Mail ID" in check:
            mail_error="Enter valid Mail ID" 
            return render_template("sign_up.html",mail_error=mail_error)
        if "Mail id exist" in check :
            mail_error2="Mail id exist"
            return render_template("sign_up.html",mail_error2=mail_error2)
        if "Inserted into DB" in check:
            mail_send=f"Confirmation mail has been sent to {mail}"
            return render_template("sign_up.html",mail_send=mail_send)
        # else:
        #     return render_template("sign_up.html")


@app.route('/resetpassworddetails', methods=["POST"])
def reset_pass():
    obj=Login()
    if request.method == "POST":
        name=request.form.get("name")
        mail=request.form.get("mail")
        password=request.form.get("password")
        confirm_pass=request.form.get("confirm_pass")
        check_detail=obj.reset_password_details(name,mail,password,confirm_pass)
        if "User does not exist" in check_detail:
            user_error='User does not exist'
            return render_template("forget_pass_details.html",user_error=user_error)
        if "Enter valid password" in check_detail:
            pass_error2='Enter valid password'
            return render_template("forget_pass_details.html",pass_error2=pass_error2)
        if "Password does not match" in check_detail:
            pass_error='Password does not match' 
            return render_template("forget_pass_details.html",pass_error=pass_error)
        if "Old password should not be the new password" in check_detail:
            pass_error3='Old password should not be the new password'
            return render_template("forget_pass_details.html",pass_error3=pass_error3)
        if "Updated" in check_detail:
            pass_update='Password Updated'
            # return redirect(url_for('index'))
            return render_template("login.html",pass_update=pass_update)
        # else:
        #     return redirect(url_for('show_reset'))


@app.route('/reset')
def show_reset():
    return render_template("forget_pass_details.html")

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
                return render_template("login.html",error1=error)
                
        else:
            error2='Invalid username or password'
            # return redirect(url_for('index'))
            return render_template("login.html",error2=error2)

@app.route('/home')
def home_page():
    return f"Welcome"

@app.route('/admin')
def hello_admin():
    obj=UserDb()
    store=obj.fetch()
    return render_template("table.html", details=store,length=len(store))

@app.route('/user/<name>')
def hello_user(name):
   if name =='admin':
       print(url_for('hello_admin'))
       return redirect(url_for('hello_admin'))
   else:
       return redirect(url_for('hello_guest',guest = name))
if __name__ == '__main__':
   app.run(debug = True)


