from flask import Flask, redirect, url_for,render_template,request,flash,session,Blueprint
from libs.UserDb import UserDb
from login_parameter import Login,Image_upload
from loggers import Loggers
from configparser import ConfigParser
import logging
import urllib.request
import os
import boto3
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from zipfile import ZipFile
import json
 
app = Flask(__name__)

# UPLOAD_FOLDER = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH']=1024*1024
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

Loggers.loggers()
logger = logging.getLogger()

inventory=Blueprint("inventory",__name__,template_folder="templates")

@inventory.route('/inventory_details')
def inventory_details():
    if not session.get('admin_logged'):
        return redirect(url_for('login.index'))
    else:
        return redirect(url_for('inventory.inventory_page'))

@inventory.route('/inventory',methods=["GET","POST"])
def inventory_page():
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            obj=UserDb()
            obj2=Login()
            obj3=Image_upload()
            if request.method=="GET":
                search=request.args.get("search")
                sort=request.args.get("sort")
                page=request.args.get('page',1,type=int)
                empty_list=[]
                if search:
                    search=obj2.inventory_search(search,page)
                    search1=list(search[1][0])
                    url=obj3.display_from_s3(search[1][0][5])
                    search1.append(url)
                    empty_list.append(search1)
                    return render_template("inventory_page.html",name=name,length=search[0],item_on_page=empty_list,total_page=search[2],page=page)
                # if sort:
                #     sort=obj2.inventory_sort(sort,page)
                #     return render_template("inventory_page.html",name=name,length=sort[0],item_on_page=sort[1],total_page=sort[2],page=page)
                else:
                    store=obj.inventory_show()
                    page=request.args.get('page',1,type=int)
                    per_page=4
                    start=(page -1) * per_page
                    end=start+per_page
                    total_page=(len(store)+per_page-1) // per_page
                    item_on_page=store[start:end]
                    item_on_page=list(item_on_page)
                    empty_list=[]
                    for item in item_on_page:
                        item=list(item)
                        filename=item[5]
                        url=obj3.display_from_s3(filename)
                        item.append(url)
                        empty_list.append(item)
                    return render_template("inventory_page.html",name=name,length=len(store),item_on_page=empty_list,total_page=total_page,page=page,url=url)
    except Exception as e:
        name=session.get('name')
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return render_template("inventory_page.html",name=name,length=len(store),item_on_page=empty_list,total_page=total_page,page=page)
        # return f"error -> {e}"

@inventory.route('/inven_add')
def inven_add():
    name=request.args.get('name')
    if not session.get('admin_logged'):
        return redirect(url_for('login.index'))
    else:
        obj=UserDb()
        category=obj.fetch_category()
        vendor=obj.get_vendor_id_name()
        name=session.get('name')
        return render_template("inventory_add.html",name=name,category=category,vendor=vendor)

@inventory.route('/inventory_add',methods=["GET","POST"])
def inventory_add():
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            obj=UserDb()
            obj2=Login()
            obj3=Image_upload()
            if request.method=="POST":
                category=request.form.get("category")
                product_brand=request.form.get("product_brand")
                product_name=request.form.get("product_name")
                description=request.form.get("description")
                quantity=request.form.get("quantity")
                price=request.form.get("price")
                features=request.form.get("features")
                vendor=request.form.get("vendor")
                features_list = features.split(',')
                product_id=obj.inventory_add(category,product_brand,product_name,description,quantity,price,features_list,vendor)
                if 'zipfile' not in request.files:
                    flash("No file part","danger")
                    logger.warning("No file part")
                    return redirect(url_for('inventory.inven_add'))
                zipfile = request.files['zipfile']
                if zipfile.filename=='':
                    flash('No image selected for uploading')
                    logger.warning("No image selected for uploading")
                    return redirect(url_for('inventory.inven_add'))
                if not zipfile.filename.lower().endswith('.zip'):
                    flash("Submit a zip file. The submitted file is not a zip file.","danger")
                    return redirect(url_for('inventory.inven_add'))
                else:
                    with ZipFile(zipfile,'r') as zip:
                        filelist=[]
                        for name in zip.namelist():
                            if name and allowed_file(name):
                                filelist.append(zip.open(name))
                            else:
                                flash("Allowed image types are - png, jpg, jpeg","danger")
                                return redirect(url_for('inventory.inven_add'))
                        filename=obj3.bucket_save_image(filelist,product_id)
                        store=obj.add_image_filename(product_id,filename)
                        flash("New Item Added","success")
                        return redirect(url_for('inventory.inventory_page'))
    except RequestEntityTooLarge:
        flash("File too large. Max size is 1MB.", "danger")
        logger.error("File too large. Max size is 1MB.")
        logger.debug("Full traceback below:", exc_info=True)
        return redirect(url_for('inventory.inven_add'))
    except Exception as e:
        flash(f"Enter correct details","danger")
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return redirect(url_for('inventory.inven_add'))

@inventory.route('/delete_item/<product_id>')
def delete_item(product_id):
    if not session.get('admin_logged'):
        return redirect(url_for('login.index'))
    else:
        obj=UserDb()
        result=obj.inventory_delete(product_id)
        return redirect(url_for('inventory.inventory_page'))

@inventory.route('/view_item/<product_id>')
def view_item(product_id):
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            obj = UserDb()
            obj2=Image_upload()
            result = obj.product_id_check(product_id)
            if result:
                url=obj2.display_from_s3(result[9])
                return render_template("view_products.html",name=name,product_id=result[0],category_name=result[10],product_brand=result[2],product_name=result[3],quantity=result[4],price=result[5],features=result[6],vendor=result[11],description=result[8],url=url)
            return render_template("view_products.html",image=image,name=name)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return redirect(url_for('login.inventory_page'))

@inventory.route('/edit_inventory/<product_id>')
def edit_inventory(product_id):
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            obj = UserDb()
            obj2=Image_upload()
            result = obj.product_id_check(product_id)
            category=obj.fetch_category()
            vendor=obj.get_vendor_id_name()
            features = result[6]
            features_str = ','.join(features)
            if result:
                url=obj2.display_from_s3(result[9])
                return render_template("inventory_edit.html",name=name,category=category,vendor=vendor,product_id=result[0],category_name=result[10],category_id=result[1],product_brand=result[2],product_name=result[3],quantity=result[4],price=result[5],features=features_str,vendor_name=result[11],vendor_id=result[7],description=result[8],url=url)
            return render_template("inventory_edit.html",url=url,name=name)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"Something went wrong ->{e}"
        # return redirect(url_for('inventory.inventory_page'))

@inventory.route('/inventory_edit', methods=["POST"])
def inventory_edit():
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            obj = UserDb()
            obj2 = Login()
            obj3=Image_upload()
            product_id = request.form.get("product_id")
            category=request.form.get("category")
            product_brand=request.form.get("product_brand")
            name = request.form.get("product_name")
            quantity = request.form.get("quantity")
            price = request.form.get("price")
            feature=request.form.get("features")
            features = feature.split(',')
            vendor=request.form.get("vendor")
            description = request.form.get("description")
            check = obj2.inventory_edit(product_id)
            if "NO" in check:
                error = "Enter a valid Product ID"
                logger.warning("Enter a valid Product ID")
                return render_template("inventory_edit.html",name=name,error=error)
            elif "Exist" in check:
                if category:
                    obj.inventory_edit_category(product_id,category)
                if product_brand:
                    obj.inventory_edit_brand(product_id,product_brand)
                if name:
                    obj.inventory_edit_name(product_id, name)
                if quantity:
                    obj.inventory_edit_quantity(product_id, quantity)
                if price:
                    obj.inventory_edit_price(product_id, price)
                if features:
                    obj.inventory_edit_features(product_id,features)
                if vendor:
                    obj.inventory_edit_vendor(product_id,vendor)
                if description:
                    obj.inventory_edit_description(product_id, description)
                zipfile = request.files.get('zipfile')
                if zipfile and zipfile.filename:
                    if not zipfile.filename.lower().endswith('.zip'):
                        flash("Submit a zip file. The submitted file is not a zip file.","danger")
                        return redirect(url_for('inventory.edit_inventory',product_id=product_id))
                    else:
                        with ZipFile(zipfile,'r') as zip:
                            filelist=[]
                            for name in zip.namelist():
                                if name and allowed_file(name):
                                    filelist.append(zip.open(name))
                                else:
                                    flash("Allowed image types are - png, jpg, jpeg","danger")
                                    return redirect(url_for('inventory.edit_inventory',product_id=product_id))
                            filename=obj3.bucket_save_image(filelist,product_id)
                            obj.inventory_edit_image(product_id,filename)
                            flash("Updated", "success")
                            logger.info("Updated")
                            return redirect(url_for('inventory.inventory_page'))
                flash("Updated", "success")       
                logger.info("Updated")
                return redirect(url_for('inventory.inventory_page'))
    except Exception as e:
        flash("Check and enter correct details","danger")
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"Something wrong -> {e}"
        # return redirect(url_for('inventory.edit_inventory',product_id=product_id))

@inventory.route('/category_list')
def category_list():
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
                category_search=obj2.category_search(search,page)
                return render_template("category_list.html",length=category_search[0],item_on_page=category_search[1],total_page=category_search[2],page=page,name=name)
            else:
                fetch_category=obj.fetch_category()
                per_page=10
                start=(page-1)*per_page
                end=start+per_page
                total_page=(len(fetch_category)+per_page-1)//per_page
                item_on_page=fetch_category[start:end]
                return render_template("category_list.html",length=len(fetch_category),item_on_page=item_on_page,total_page=total_page,page=page,name=name)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        # return render_template("vendor_list.html")
        return f"vendor list error -->>==>> {e}"

@inventory.route('/add_category',methods=["GET"])
def add_category():
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            return render_template("category_add.html",name=name)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"vendor list error -->>==>> {e}"

@inventory.route('/category_add',methods=["POST"])
def category_add():
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            obj=UserDb()
            obj2=Login()
            if request.method=="POST":
                category_name=request.form.get('category_name')
                category=obj2.get_category(category_name)
                if category=="NO":
                    name_error="Category already exists"
                    return render_template("category_add.html",name_error=name_error,name=name)
                else:
                    obj.add_category(category_name)
                    flash("Category Added","success")
                    return redirect(url_for("inventory.category_list"))
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"vendor list error -->>==>> {e}"

@inventory.route('/category_delete/<category_id>')
def category_delete(category_id):
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            obj=UserDb()
            result=obj.category_delete(category_id)
            flash("Category Deleted","success")
            return redirect(url_for('inventory.category_list'))
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"vendor list error -->>==>> {e}"

@inventory.route('/category_edit/<category_id>')
def category_edit(category_id):
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            obj=UserDb()
            result=obj.category_by_id(category_id)
            return render_template("category_edit.html",category_id=result[0][0],category_name=result[0][1],name=name)
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"vendor list error -->>==>> {e}"

@inventory.route('/edit_category',methods=["POST"])
def edit_category():
    try:
        if not session.get('admin_logged'):
            return redirect(url_for('login.index'))
        else:
            name=session.get('name')
            category_id=request.form.get("category_id")
            category_name=request.form.get("category_name")
            print(f"cat id ->{category_id}")
            print(f"cat name ->{category_name}")
            obj=UserDb()
            category=obj.check_category(category_name,category_id)
            if category =="YES":
                category_edit=obj.category_edit(category_name,category_id)
                flash("Updated","success")
                return redirect(url_for('inventory.category_list'))
            else:
                flash("Category already exists","danger")
                return redirect(url_for('inventory.edit_category'))
    except Exception as e:
        logger.error(f"error -> {e}")
        logger.debug("Full traceback below:", exc_info=True)
        return f"Category list error -->>==>> {e}"



