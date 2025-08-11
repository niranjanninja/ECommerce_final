from flask import Flask, redirect, url_for,render_template,request,flash,session,Blueprint
from libs.UserDb import UserDb
# from itsdangerous import URLSafeTimedSerializer,SignatureExpired
from login_parameter import Login,Image_upload
from loggers import Loggers
from configparser import ConfigParser
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE
import logging

app = Flask(__name__)

Loggers.loggers()
logger = logging.getLogger()

admin=Blueprint("admin",__name__,template_folder="templates")

@admin.route('/admin')
def hello_admin():
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            obj=UserDb()
            obj2=Login()
            name=session.get('name')
            search=request.args.get('search')
            sort=request.args.get('sort')
            page=request.args.get('page',1,type=int)
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
                return render_template("table.html",length=len(search_name_mail_num),item_on_page=item_on_page,total_page=total_page,page=page,name=name)
            if sort:
                sort=obj2.admin_sort(sort,page)
                return render_template("table.html",length=sort[0],item_on_page=sort[1],total_page=sort[2],page=page,name=name)
            else:
                store=obj.fetch()
                page=request.args.get('page',1,type=int)
                per_page=13
                start=(page-1)*per_page
                end=start+per_page
                total_page=(len(store)+per_page-1)//per_page
                item_on_page=store[start:end]
                return render_template("table.html",length=len(store),item_on_page=item_on_page,total_page=total_page,page=page,name=name)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"Something went wrong"


@admin.route('/vendor_add',methods=["GET","POST"])
def vendor_add():
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            country_code_list = []
            for code, regions in COUNTRY_CODE_TO_REGION_CODE.items():
                for region in regions:
                    country_code_list.append((region, code))
                    break
            country_code_list.sort()
            if request.method == "GET":
                return render_template("vendor_add.html", country_codes=country_code_list,name=name)
            name=session.get('name')
            obj=Login()
            if request.method=="POST":
                vendor_name=request.form.get("vendor_name")
                address=request.form.get("address")
                number=request.form.get("number")
                country_code = request.form.get("country_code")
                mail_id=request.form.get("mail_id")
                full_number = country_code + number
                vendor=obj.get_vendor_details(vendor_name,address,full_number,mail_id)
                if "Vendor exists" in vendor:
                    name_error="Vendor name already exists"
                    logger.warning("Vendor name already exists")
                    return render_template("vendor_add.html",name_error=name_error,country_codes=country_code_list,name=name)
                if "Address exist" in vendor:
                    address_error="Vendor address already exists"
                    logger.warning("Vendor address already exists")
                    return render_template("vendor_add.html",address_error=address_error,country_codes=country_code_list,name=name)
                if "Enter valid number" in vendor:
                    num_error="Enter valid Number"
                    logger.warning("Enter valid number")
                    return render_template("vendor_add.html",num_error=num_error,country_codes=country_code_list,name=name)
                if "Number exist" in vendor:
                    num_error2="Vendor number already exists"
                    logger.warning("Vendor number already exist")
                    return render_template("vendor_add.html",num_error2=num_error2,country_codes=country_code_list,name=name)
                if "Mail not valid" in vendor:
                    mail_error="Enter a valid Mail ID"
                    logger.warning("Mail not valid")
                    return render_template("vendor_add.html",mail_error=mail_error,country_codes=country_code_list,name=name)
                if "Mail Exist" in vendor:
                    mail_error2="Vendor Mail ID already exists"
                    logger.warning("Mail ID already Exist")
                    return render_template("vendor_add.html",mail_error2=mail_error2,country_codes=country_code_list,name=name)
                if "Added" in vendor:
                    flash("Vendor Added","success")
                    return redirect(url_for("admin.vendor_list"))
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        # return redirect(url_for('vendor_add'))
        return f"Error=>{e}"

@admin.route('/vendor_list')
def vendor_list():
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            search=request.args.get('search')
            page=request.args.get('page',1,type=int)
            obj=UserDb()
            obj2=Login()
            if search:
                vendor_search=obj2.vendor_search(search,page)
                return render_template("vendor_list.html",length=vendor_search[0],item_on_page=vendor_search[1],total_page=vendor_search[2],page=page,name=name)
            else:
                fetch_vendor=obj.fetch_vendor()
                per_page=10
                start=(page-1)*per_page
                end=start+per_page
                total_page=(len(fetch_vendor)+per_page-1)//per_page
                item_on_page=fetch_vendor[start:end]
                return render_template("vendor_list.html",length=len(fetch_vendor),item_on_page=item_on_page,total_page=total_page,page=page,name=name)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        # return render_template("vendor_list.html")
        return f"vendor list error -->>==>> {e}"

@admin.route('/vendor_delete/<vendor_id>')
def vendor_delete(vendor_id):
    if not session.get('admin_logged'):
        return redirect(url_for('login.index'))
    else:
        obj=UserDb()
        result=obj.vendor_delete(vendor_id)
        flash("Vendor Deleted","success")
        return redirect(url_for('admin.vendor_list'))

@admin.route('/edit_vendor/<vendor_id>')
def edit_vendor(vendor_id):
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            obj=UserDb()
            obj2=Login()
            name=session.get('name')
            country_code_list = []
            result=obj.fetch_vendor_on_id(vendor_id)
            return render_template("vendor_edit.html",vendor_id=result[0],vendor_name=result[1],address=result[2],number=result[3],mail_id=result[4],name=name)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"Errro ->{e}"

@admin.route('/vendor_edit',methods=["POST"])
def vendor_edit():
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            obj=UserDb()
            vendor_id=request.form.get("vendor_id")
            vendor_name=request.form.get("vendor_name")
            address=request.form.get("address")
            number=request.form.get("number")
            mail_id=request.form.get("mail_id")
            vendor=obj.check_vendor_by_id(vendor_id)
            if "ok" in vendor:
                if vendor_name:
                    result1=obj.check_vendor_name(vendor_name,vendor_id)
                    if result1=="yes":
                        flash("Vendor name already exists","danger")
                        return redirect(url_for('admin.edit_vendor',vendor_id=vendor_id))
                    else:
                        obj.update_vendor_name(vendor_name,vendor_id)
                if address:
                    result2=obj.check_vendor_address(address,vendor_id)
                    if result2=="yes":
                        flash("Vendor address already exists","danger")
                        return redirect(url_for('admin.edit_vendor',vendor_id=vendor_id))
                    else:
                        obj.update_vendor_address(address,vendor_id)
                if number:
                    result3=obj.check_vendor_number(number,vendor_id)
                    if result3=="yes":
                        flash("Vendor number already exists","danger")
                        return redirect(url_for('admin.edit_vendor',vendor_id=vendor_id))
                    else:
                        obj.update_vendor_number(number,vendor_id)
                if mail_id:
                    result4=obj.check_vendor_mail(mail_id,vendor_id)
                    if result4=="yes":
                        flash("Vendor mail ID already exists","danger")
                        return redirect(url_for('admin.edit_vendor',vendor_id=vendor_id))
                    else:
                        obj.update_vendor_mail_id(mail_id,vendor_id)
                flash("Updated","success")
                return redirect(url_for('admin.vendor_list'))
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"Errro ->{e}"
