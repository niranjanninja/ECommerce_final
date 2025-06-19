from libs.UserDb import UserDb
import re
import bcrypt
import smtplib
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime 
 

logger=logging.getLogger()
logger.setLevel(logging.INFO)
log_filename = datetime.now().strftime("logs/%d-%m-%Y.log")
handler=TimedRotatingFileHandler(filename = log_filename,when = "midnight", interval = 1 , backupCount = 7)
handler.setLevel(logging.ERROR)
handler.setLevel(logging.WARNING)
formatter=logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

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
                    logger.warning("Username  does not exist")
                    return f"User does not exist"
                    # print("User does not exist" )
            else:
                logger.warning("User does not exist")
                # print("User does not exist")
                return f"User does not exist"
        except Exception as e:
            logger.error(f"Something went wrong -> {e} ")

    def get_all_details(self,name,password,confirm_password,number,mail):
        try:
            pass_pattern = r'\w{10,100}$' 
            phn_pattern = r'^\d{10}$'
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
                                        # return f"Inserted into DB"
                                        # print("Inserted in db")
                                        # sender="niranjanrox56@gmail.com" 
                                        # receiver=(mail)
                                        # message=f"Hello {name}\n Welcome to our website"
                                        # server=smtplib.SMTP("smtp.gmail.com",587)
                                        # server.starttls()
                                        # server.login(sender,'jaxa cqze rzza hvyj')
                                        # server.sendmail(sender,receiver,message)
                                        # print(f"Email has been sent to {mail}")
                                        # print("Inserted in db")
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

# obj=Login()
# obj.check_password("ninja","ninja")
# obj=Login()
# obj.reset_password_details("Niranjan","ninja@gmail.com","niranjanninja","niranjanninja")
# obj=Login()
# obj.get_all_details("Niranjan","ninjaninja","ninjaninja","8754826711","niranjansabari56@gmail.com")
