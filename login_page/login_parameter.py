from libs.UserDb import UserDb
import re
import smtplib
import bcrypt
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime  
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE
import urllib.request
import os
import boto3
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from pathlib import Path
from datetime import timedelta
from configparser import ConfigParser

file='/home/ubuntu/projectsql/login_page/libs/config.ini'
config=ConfigParser()
config.read(file)

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

class Login:
    def __init__(self):
        self.user_db_obj = UserDb() 

    
    def reset_password_details(self,name,mail,password,confirm_pass):
        try:
            obj=UserDb()
            mail_pattern =r'^[a-z A-Z 0-9]+[\._]?[a-z A-Z 0-9]+[@]\w+[.]\D{2,3}$'
            pass_pattern = r'\w{10,100}$'
            if re.search(mail_pattern,mail):
                result = self.user_db_obj.get_user_by_name_email(name, mail)
                if result:
                    if re.search(pass_pattern,password):
                        if password == confirm_pass:
                            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                            check_hash=obj.get_user_by_name(name)
                            if not bcrypt.checkpw(password.encode('utf-8'),check_hash.encode('utf-8')):
                                self.user_db_obj.update_user_by_name_email(hashed,name,mail)
                                return f"Updated"
                                # print("Updated")
                            else:
                                logger.warning("Old password should not be the new password")
                                # print("Old password should not be the new password")
                                return f"Old password should not be the new password"
                        else:
                            logger.warning("Password does not match")
                            return f"Password does not match"
                            # print("Password does not match")
                    else:
                        logger.warning("Enter valid password")
                        return f"Enter valid password"
                        # print("Enter valid password")
                else:
                    logger.warning("Username/Mail ID does not exist")
                    return f"Username/Mail ID does not exist"
                    # print("User does not exist" )
            else:
                logger.warning("Username/Mail ID does not exist")
                # print("User does not exist")
                return f"Username/Mail ID does not exist"
        except Exception as e:
            logger.error(f"Something went wrong -> {e} ")

    def inventory_check_add(self,product_id):
        result=self.user_db_obj.product_id_check(product_id)
        if result:
            # print("Exist")
            return f"Exist"
        else:
            # print("NO")
            return f"NO"

    def inventory_delete(self,product_id):
        result=self.user_db_obj.product_id_check(product_id)
        if result:
            execute=self.user_db_obj.inventory_delete(product_id)
            # print("Item Deleted")
            return f"Item Deleted"
        else:
            # print("Enter correct product ID")
            return f"NO"

    def inventory_edit(self,product_id):
        result=self.user_db_obj.product_id_check(product_id)
        if result:
            return f"Exist"
        else:
            # print("NO")
            return f"NO"

    def get_vendor_details(self,vendor_name,address,full_number,mail_id):
        try:
            obj=UserDb()
            phn_pattern = r'^\+\d{10,15}$'
            mail_pattern = r'^[a-z A-Z 0-9]+[\._]?[a-z A-Z 0-9]+[@]\w+[.]\D{2,3}$'
            result=obj.get_vendor_name(vendor_name)
            if not result:
                result2=obj.get_vendor_address(address)
                if not result2:
                    if re.search(phn_pattern,full_number):
                        result3=obj.get_vendor_number(full_number)
                        if not result3:
                            if re.search(mail_pattern,mail_id):
                                result4=obj.get_vendor_mail(mail_id)
                                if not result4:
                                    obj.vendor_add(vendor_name,address,full_number,mail_id)
                                    return f"Added"
                                else:
                                    logger.warning("Vendor mail id already exist" )
                                    return f"Mail Exist"
                            else:
                                logger.warning("Mail id is not valid" )
                                return f"Mail not valid"
                        else:
                            logger.warning("Vendor phone number already exist" )
                            return f"Number exist"
                    else:
                        logger.warning("Phone number is not valid" )
                        print("Enter valid no")
                        return f"Enter valid number"
                else:
                    logger.warning("Vendor address already exist" )
                    return f"Address exist"
            else:
                logger.warning("Vendor name already exist" )
                return f"Vendor exists"
        except Exception as e:
            logger.error(f"Something went wrong ->{e}")


    def get_all_details(self,name,password,confirm_password,number,mail):
        try:
            pass_pattern = r'\w{10,100}$' 
            phn_pattern = r'^\+\d{10,15}$'
            mail_pattern = r'^[a-z A-Z 0-9]+[\._]?[a-z A-Z 0-9]+[@]\w+[.]\D{2,3}$'
            result = self.user_db_obj.get_user_by_name(name)
            if not result:
                # print("NO NAME")
                if password==confirm_password:
                    if re.search(pass_pattern,password):
                        hashed=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        # print("CORRECT")
                        if re.search(phn_pattern,number):
                            result2=self.user_db_obj.get_number(number)
                            if not result2:
                                # print("NO NUM")
                                if re.search(mail_pattern,mail):
                                    result3=self.user_db_obj.get_mail(mail)
                                    if not result3:
                                        # print("NOMAIL")
                                        user_details=self.user_db_obj.insert_values_into_table(name,hashed,hashed,number,mail)
                                        return f"Inserted into DB"
                                    else:
                                        logger.warning("Mail id exist" )
                                        return f"Mail id exist"
                                        # print("Mail exist")
                                else:
                                    logger.warning("Enter valid Mail ID" )
                                    return f"Enter valid Mail ID"
                                    # print("Valid mail enter")
                            else:
                                logger.warning("Number already exist")
                                return f"Number already exist"
                                # print("Number exist")
                        else:
                            logger.warning("Enter valid number")
                            return f"Enter valid number"
                            # print("Enter valid num")
                    else:
                        logger.warning("Enter valid password" )
                        return f"Enter valid password"
                        # print("Enter valid pass")
                else:
                    logger.warning("Password does not match" )
                    return f"Password does not match"
                    # print("Pass no match")
            else:
                logger.warning("Username already exist")
                return f"Username already exist"
                # print("User exist")
        except Exception as e:
            logger.error(f"Something went wrong -> {e} ")

    def local_save_image(self,file,product_id):
        try:
            UPLOAD_FOLDER = 'static/uploads'
            app.config['MAX_CONTENT_LENGTH']=1024*1024
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            filename=f"product_id{product_id}.jpg"
            Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return filename
        except Exception as e:
            logger.error(f"error -> {e}")

    def get_category(self,category_name):
        try:
            obj=UserDb()
            name=obj.get_category(category_name)
            if name=="NO":
                return "NO"
            else:
                return "YES"
        except Exception as e:
            logger.error(f"error -> {e}")

    def vendor_search(self,search,page):
        try:
            obj=UserDb()
            if search.isdigit():
                search_id=obj.vendor_search_id(search)
                per_page=13
                start=(page-1)*per_page
                end=start+per_page
                total_page=(len(search_id)+per_page-1)//per_page
                item_on_page=search_id[start:end]
                return [len(search_id),list(item_on_page),total_page]
            else:
                search_vendor=obj.vendor_search(search)
                per_page=13
                start=(page-1)*per_page
                end=start+per_page
                total_page=(len(search_vendor)+per_page-1)//per_page
                item_on_page=search_vendor[start:end]
                return [len(search_vendor),list(item_on_page),total_page]
        except Exception as e:
            print(f"ERROR +> {e}")


    def category_search(self,search,page):
        try:
            obj=UserDb()
            if search.isdigit():
                search_id=obj.category_by_id(search)
                per_page=4
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(search_id)+per_page-1) // per_page
                item_on_page=search_id[start:end]
                return [len(search_id),list(item_on_page),total_page]
            elif search:
                search_name=obj.category_by_name(search)
                per_page=4
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(search_name)+per_page-1) // per_page
                item_on_page=search_name[start:end]
                # print([len(search_name),item_on_page,total_page])
                # print(item_on_page)
                return [len(search_name),item_on_page,total_page]
        except Exception as e:
            print(f"Error -> {e}")

    def inventory_search(self,search,page):
        try:
            obj=UserDb()
            if search.isdigit():
                search_id=obj.inventory_by_id(search)
                per_page=4
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(search_id)+per_page-1) // per_page
                item_on_page=search_id[start:end]
                return [len(search_id),list(item_on_page),total_page]
            elif search:
                search_name=obj.inventory_by_name(search)
                per_page=4
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(search_name)+per_page-1) // per_page
                item_on_page=search_name[start:end]
                # print([len(search_name),item_on_page,total_page])
                # print(item_on_page)
                return [len(search_name),item_on_page,total_page]
        except Exception as e:
            print(f"Error -> {e}")

    def homepage_search(self,search,page):
        try:
            obj=UserDb()
            if search:
                search=obj.homepage_search(search)
                per_page=6
                start=(page-1)*per_page
                end=start+per_page
                total_page=(len(search)+per_page-1)//per_page
                item_on_page=search[start:end]
                # print([len(search),item_on_page,total_page])
                return([len(search),item_on_page,total_page])
            else:
                return f"something went wrong"
        except Exception as e:
            print(f"Error -> {e}")


    def admin_sort(self,sort,page):
        try:
            obj=UserDb()
            if sort=='username_asc':
                username_asc=obj.sort_user_name_asc()
                per_page=13
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(username_asc)+per_page-1) // per_page
                item_on_page=username_asc[start:end]
                return [len(username_asc),item_on_page,total_page]
            elif sort=='username_desc':
                username_desc=obj.sort_user_name_desc()
                per_page=13
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(username_desc)+per_page-1) // per_page
                item_on_page=username_desc[start:end]
                return [len(username_desc),item_on_page,total_page]
            elif sort=='usernumber_asc':
                usernumber_asc=obj.sort_user_num_asc()
                per_page=13
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(usernumber_asc)+per_page-1) // per_page
                item_on_page=usernumber_asc[start:end]
                return [len(usernumber_asc),item_on_page,total_page]
            elif sort=='usernumber_desc':
                usernumber_desc=obj.sort_user_num_desc()
                per_page=13
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(usernumber_desc)+per_page-1) // per_page
                item_on_page=usernumber_desc[start:end]
                return [len(usernumber_desc),item_on_page,total_page]
            elif sort=='mailid_asc':
                mailid_asc=obj.sort_user_mail_asc()
                per_page=13
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(mailid_asc)+per_page-1) // per_page
                item_on_page=mailid_asc[start:end]
                return [len(mailid_asc),item_on_page,total_page]
            elif sort=='mailid_desc':
                mailid_desc=obj.sort_user_mail_desc()
                per_page=13
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(mailid_desc)+per_page-1) // per_page
                item_on_page=mailid_desc[start:end]
                return [len(mailid_desc),item_on_page,total_page]
        except Exception as e:
            print(f"Error -> {e}")

    def inventory_sort(self,sort,page):
        try:
            obj=UserDb()
            if sort=='id_asc':
                id_asc=obj.sort_inventory_id_asc()
                per_page=4
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(id_asc)+per_page-1) // per_page
                item_on_page=id_asc[start:end]
                # print([len(id_asc),item_on_page,total_page])
                return [len(id_asc),item_on_page,total_page]
            elif sort=='id_desc':
                id_desc=obj.sort_inventory_id_desc()
                per_page=4
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(id_desc)+per_page-1) // per_page
                item_on_page=id_desc[start:end]
                # print([len(id_desc),item_on_page,total_page])
                return [len(id_desc),item_on_page,total_page]
            elif sort=='name_asc':
                name_asc=obj.sort_inventory_name_asc()
                per_page=4
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(name_asc)+per_page-1) // per_page
                item_on_page=name_asc[start:end]
                # print([len(name_asc),item_on_page,total_page])
                return [len(name_asc),item_on_page,total_page]
            elif sort=='name_desc':
                name_desc=obj.sort_inventory_name_desc()
                per_page=4
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(name_desc)+per_page-1) // per_page
                item_on_page=name_desc[start:end]
                # print([len(name_desc),item_on_page,total_page])
                return [len(name_desc),item_on_page,total_page]
            elif sort=='quantity_asc':
                quantity_asc=obj.sort_inventory_quantity_asc()
                per_page=4
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(quantity_asc)+per_page-1) // per_page
                item_on_page=quantity_asc[start:end]
                # print([len(quantity_asc),item_on_page,total_page])
                return [len(quantity_asc),item_on_page,total_page]
            elif sort=='quantity_desc':
                quantity_desc=obj.sort_inventory_quantity_desc()
                per_page=4
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(quantity_desc)+per_page-1) // per_page
                item_on_page=quantity_desc[start:end]
                # print([len(quantity_desc),item_on_page,total_page])
                return [len(quantity_desc),item_on_page,total_page]
            elif sort=='price_asc':
                price_asc=obj.sort_inventory_price_asc()
                per_page=4
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(price_asc)+per_page-1) // per_page
                item_on_page=price_asc[start:end]
                # print([len(price_asc),item_on_page,total_page])
                return [len(price_asc),item_on_page,total_page]
            elif sort=='price_desc':
                price_desc=obj.sort_inventory_price_desc()
                per_page=4
                start=(page -1) * per_page
                end=start+per_page
                total_page=(len(price_desc)+per_page-1) // per_page
                item_on_page=price_desc[start:end]
                # print([len(price_desc),item_on_page,total_page])
                return [len(price_desc),item_on_page,total_page]
        
        except Exception as e:
            print(f"Error -> {e}")

class Image_upload:
    # def __init__(self):
    #     self.user_db_obj = UserDb()

    
    def bucket_save_image(self,filelist,product_id):
        try:
            s3 = boto3.client('s3',
                              aws_access_key_id=config['AWS']['aws_access_key_id'],
                              aws_secret_access_key=config['AWS']['aws_secret_access_key'],
                              region_name=config['AWS']['region_name']
                              )
            bucket_name = "webpage.image.upload"
            # print(f"filelist ->{filelist}")
            filename = []
            index = 1
            for i in filelist:
                file = f"images/product_id{product_id}_{index}.jpg"
                # print(file)
                s3.upload_fileobj(i, bucket_name, file)
                # print("uploaded")
                filename.append(file)
                index=index+1
            # print(f"filename -> {filename}")
            return filename
        except Exception as e:
            # print(f"error ->{e}")
            return f"Something went wrong {e}"
            logger.error(f"Error uploading to S3: {e}")
            # return None

    def display_from_s3(self,filename):
        try:
            s3 = boto3.client('s3',
                              aws_access_key_id=config['AWS']['aws_access_key_id'],
                              aws_secret_access_key=config['AWS']['aws_secret_access_key'],
                              region_name=config['AWS']['region_name'])
            url=[]
            for i in filename:
                url_generate= s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': 'webpage.image.upload', 'Key': i},
                    ExpiresIn=600)
                url.append(url_generate)
            return url
        except Exception as e:
            logger.error(f"Error generating presigned GET URL: {e}")
            return None

# obj2=Image_upload()
# obj2.bucket_save_image(['monitor1.jpg', 'monitor2.jpg', 'keyboard2.jpg', 'keyboard3.jpg'],'1')
# obj2.display_from_s3('images/product_id15_1.jpg', 'images/product_id15_2.jpg', 'images/product_id15_3.jpg', 'images/product_id15_4.jpg')
# images/product_id36.jpg,
# images/product_id32.jpg,
# images/product_id37.jpg,
# images/product_id29.jpg,
# images/product_id34.jpg,
# images/product_id38.jpg,
# images/product_id35.jpg)

# obj=Login()
# obj.get_vendor_details('Niranjan3','28,Chennai-9','+918974636728','vendorninja1@gmail.com')
# obj=Login()
# obj.homepage_search("keyboard",1)
# obj=Login()
# obj.reset_password_details("Niranjan","ninja@gmail.com","niranjanninja","niranjanninja")
# obj=Login()
# obj.get_all_details("Niranjan","ninjaninja","ninjaninja","8754826711","niranjansabari56@gmail.com")
