from libs.DBConnect import DBConnect
# from DBConnect import DBConnect
class UserDb:

    def __init__(self):
        self.db_obj = DBConnect()
        self.db_connect = self.db_obj.check_db_connection()
        if self.db_connect['status']:
            self.conn = self.db_connect['data']
            self.curr=self.conn.cursor()
        else:
            print(self.db_connect['status'])

    def get_user_by_name_email(self,name,mail):
        querry=f"SELECT * from sign_up_page WHERE user_name = '{name}' AND mail_id = '{mail}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        # print(result)
        return result

    def get_user_by_name(self,name):
        querry=f"SELECT * FROM sign_up_page WHERE user_name = '{name}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        if result:
            return result[1]
        else:
            pass

    def get_name(self,name):
        querry=f"SELECT * FROM sign_up_page WHERE user_name='{name}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        if result:
            return result[0]
        else:
            pass

    def get_mail(self,mail):
        querry=f"SELECT * FROM sign_up_page WHERE mail_id='{mail}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        if result:
            return result[2]
        else:
            pass

    def get_number(self,number):
        querry=f"SELECT * FROM sign_up_page WHERE phone_number='{number}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        if result:
            return result[3]
        else:
            pass

    def update_user_by_name_email(self,password, name, mail):
        querry=f"UPDATE sign_up_page SET user_pass = '{password}' WHERE user_name='{name}' AND mail_id = '{mail}'"
        self.curr.execute(querry)
        self.conn.commit()


    def get_user_by_name_pass(self,name,password):
        querry=f"SELECT * FROM sign_up_page WHERE user_name = '{name}' AND user_pass = '{password}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def update_user_by_name_pass(self,name,password):
        querry=f"UPDATE sign_up_page SET user_name = '{name}' WHERE user_pass = '{password}'"
        self.curr.execute(querry)
        self.conn.commit()

    def update_user_by_pass_name(self,password,name):
        querry=f"UPDATE sign_up_page SET user_pass='{password}' WHERE user_name = '{name}'"
        self.curr.execute(querry)
        self.conn.commit()

    def update_user_by_num_name(self,new_num,name):
        querry = f"UPDATE sign_up_page SET phone_number='{new_num}' WHERE user_name='{name}'"
        self.curr.execute(querry)
        self.conn.commit()

    def update_user_by_mail_name(self,new_mail,name):
        querry=f"UPDATE sign_up_page SET mail_id = '{new_mail}' WHERE user_name='{name}'"
        self.curr.execute(querry)
        self.conn.commit()

    def check_user_by_name(self,name):
        querry=f"SELECT * FROM sign_up_page WHERE user_name = '{name}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def check_user_by_number(self,num):
        querry=f"SELECT * from sign_up_page WHERE phone_number = '{num}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def check_user_by_mail(self,mail):
        querry=f"SELECT * FROM sign_up_page WHERE mail_id = '{mail}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def insert_into_table(self,name,password,num,mail):
       querry=f"INSERT INTO sign_up_page (user_name,user_pass,phone_number,mail_id) VALUES ('{name}','{password}','{num}','{mail}')"
       self.curr.execute(querry)
       self.conn.commit()

    def fetch(self):
        querry=f"SELECT * FROM sign_up_page"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def insert_values_into_table(self,name,password,confirm_password,number,mail):
        querry=f"INSERT INTO sign_up_page (user_name,user_pass,phone_number,mail_id) VALUES ('{name}','{password}','{number}','{mail}')"
        self.curr.execute(querry)
        self.conn.commit()


# obj=UserDb()
# obj.get_number("8754826711")
# obj=UserDb()
# obj.get_user_by_name_email("Niranjan","ninja@gmail.com")
# obj=UserDb()
# obj.update_user_by_name_email("ninja","Niranjan","ninja@gmail.com")
# obj=UserDb()
# obj.get_user_by_name_email("kala","ninja@gmail.com")
