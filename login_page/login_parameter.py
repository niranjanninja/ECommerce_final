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

    def bucket_save_image(self,file,product_id):
        try:
            s3 = boto3.client('s3',
                                     aws_access_key_id=config['AWS']['aws_access_key_id'],
                                     aws_secret_access_key=config['AWS']['aws_secret_access_key'],
                                     region_name=config['AWS']['region_name']
                                     )
            bucket_name = "webpage.image.upload"
            filename = f"images/product_id{product_id}.jpg"
            # print("Uploading")
            s3.upload_fileobj(file,bucket_name,filename)
            # print("Uploaded")
            return filename
        except Exception as e:
            return f"Something went wrong {e}"
            logger.error(f"Error uploading to S3: {e}")
            # return None

    def display_from_s3(self,filename):
        try:
            s3 = boto3.client(
                    's3',
                    aws_access_key_id=config['AWS']['aws_access_key_id'],
                    aws_secret_access_key=config['AWS']['aws_secret_access_key'],
                    region_name=config['AWS']['region_name'])

            url = s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': 'webpage.image.upload', 'Key': filename},
                    ExpiresIn=600)
            return url

        except Exception as e:
            logger.error(f"Error generating presigned GET URL: {e}")
            return None


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



# obj=Login()
# obj.inventory_delete("3")
# obj=Login()
# obj.reset_password_details("Niranjan","ninja@gmail.com","niranjanninja","niranjanninja")
# obj=Login()
# obj.get_all_details("Niranjan","ninjaninja","ninjaninja","8754826711","niranjansabari56@gmail.com")
