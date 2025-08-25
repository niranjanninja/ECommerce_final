from libs.DBConnect import DBConnect
import json
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
###########################################    USER QUERRY   ########################################################

    def get_user_by_name_email(self,name,mail):
        querry=f"SELECT * from customers WHERE user_name = '{name}' AND mail_id = '{mail}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        # print(result)
        return result

    def get_user_by_mail(self,mail):
        querry=f"SELECT * from customers where mail_id='{mail}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        # print(result[0])
        return result[0]

    def get_user_by_name(self,name):
        querry=f"SELECT * FROM customers WHERE user_name = '{name}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        if result:
            return result[1]
        else:
            pass

    def get_name(self,name):
        querry=f"SELECT * FROM customers WHERE user_name='{name}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        if result:
            return result[0]
        else:
            pass

    def get_customer_id_name(self,name,hash_pass):
        querry=f"SELECT * FROM CUSTOMERS WHERE user_name='{name}' and user_pass='{hash_pass}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        if result:
            return result[6]
        else:
            pass

    def get_mail(self,mail):
        querry=f"SELECT * FROM customers WHERE mail_id='{mail}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        if result:
            return result[2]
        else:
            pass

    def get_number(self,number):
        querry=f"SELECT * FROM customers WHERE phone_number='{number}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        if result:
            return result[3]
        else:
            pass

    def update_user_by_name_email(self,password, name, mail):
        querry=f"UPDATE customers SET user_pass = '{password}' WHERE user_name='{name}' AND mail_id = '{mail}'"
        self.curr.execute(querry)
        self.conn.commit()


    def get_user_by_name_pass(self,name,password):
        querry=f"SELECT * FROM customers WHERE user_name = '{name}' AND user_pass = '{password}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def update_user_by_name_pass(self,name,password):
        querry=f"UPDATE customers SET user_name = '{name}' WHERE user_pass = '{password}'"
        self.curr.execute(querry)
        self.conn.commit()

    def update_user_by_pass_name(self,password,name):
        querry=f"UPDATE customers SET user_pass='{password}' WHERE user_name = '{name}'"
        self.curr.execute(querry)
        self.conn.commit()

    def update_user_by_num_name(self,new_num,name):
        querry = f"UPDATE customers SET phone_number='{new_num}' WHERE user_name='{name}'"
        self.curr.execute(querry)
        self.conn.commit()

    def update_user_by_mail_name(self,new_mail,name):
        querry=f"UPDATE customers SET mail_id = '{new_mail}' WHERE user_name='{name}'"
        self.curr.execute(querry)
        self.conn.commit()

    def check_user_by_name(self,name):
        querry=f"SELECT * FROM customers WHERE user_name = '{name}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def check_user_by_number(self,num):
        querry=f"SELECT * from customers WHERE phone_number = '{num}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def check_user_by_mail(self,mail):
        querry=f"SELECT * FROM customers WHERE mail_id = '{mail}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def insert_into_table(self,name,password,num,mail):
       querry=f"INSERT INTO customers (user_name,user_pass,phone_number,mail_id) VALUES ('{name}','{password}','{num}','{mail}')"
       self.curr.execute(querry)
       self.conn.commit()

    def fetch(self):
        querry=f"SELECT * FROM customers"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def insert_values_into_table(self,name,password,confirm_password,number,mail):
        querry=f"INSERT INTO customers (user_name,user_pass,phone_number,mail_id) VALUES ('{name}','{password}','{number}','{mail}')"
        self.curr.execute(querry)
        self.conn.commit()

    def confirm_mail(self,mail):
        querry=f"UPDATE customers SET confirm_mail = 'true' WHERE mail_id = '{mail}'"
        self.curr.execute(querry)
        self.conn.commit()

    def get_admin_detail(self,name):  
        querry=f"SELECT * FROM customers WHERE user_name = '{name}'" 
        self.curr.execute(querry) 
        result=self.curr.fetchone()    
        # print(type(result[5]))    
        # print(result[5])     
        return result[5]

###########################################   INVENTORY QUERRY #########################################################

    def inventory_show(self):
        querry=f"select products.product_id,products.product_name,category.category_name,products.quantity,products.price, products.images,vendors.vendor_name from products inner join vendors on products.vendor_id = vendors.vendor_id inner join category on products.category_id = category.category_id ORDER BY products.product_id"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        # print(type(result))
        return result

    def inventory_add(self,category,product_brand,product_name,description,quantity,price,features_list,vendor):
        features_json = json.dumps(features_list)
        querry=f"INSERT INTO products (category_id,product_brand,product_name,quantity,price,features,vendor_id,product_description) VALUES ('{category}','{product_brand}','{product_name}','{quantity}','{price}','{features_json}','{vendor}','{description}') returning product_id"
        self.curr.execute(querry)
        product_id = self.curr.fetchone()[0]
        self.conn.commit()
        # print(product_id)
        return product_id

    def add_image_filename(self,product_id,filename):
        querry=f"UPDATE products SET images = ARRAY{filename} WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def inventory_delete(self,product_id):
        querry=f"DELETE FROM products WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def inventory_edit_brand(self,product_id,product_brand):
        querry=f"UPDATE products SET product_brand='{product_brand}' WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def inventory_edit_category(self,product_id,category):
        querry=f"UPDATE products SET category_id='{category}' WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def inventory_edit_name(self,product_id,product_name):
        querry=f"UPDATE products SET product_name = '{product_name}' WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def inventory_edit_description(self,product_id,description):
        querry=f"UPDATE products SET product_description ='{description}' WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def inventory_edit_quantity(self,product_id,quantity):
        querry=f"UPDATE products SET quantity = '{quantity}' WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def inventory_edit_price(self,product_id,price):
        querry=f"UPDATE products SET price = '{price}' WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def inventory_edit_features(self,product_id,features):
        features_json=json.dumps(features)
        querry=f"UPDATE products SET features='{features_json}' WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def inventory_edit_vendor(self,product_id,vendor):
        querry=f"UPDATE products SET vendor_id='{vendor}' WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def inventory_edit_image(self,product_id,filename):
        querry=f"UPDATE products SET images = ARRAY{filename} WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def product_id_check(self,product_id):
        querry=f"SELECT products.*,category.category_name,vendors.vendor_name FROM products INNER JOIN vendors ON products.vendor_id=vendors.vendor_id INNER JOIN category ON products.category_id=category.category_id WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        # print(result)
        return result

    def get_admin_detail(self,name):
        querry=f"SELECT * FROM customers WHERE user_name = '{name}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        # print(type(result[5]))
        # print(result[5])
        return result[5]

    def inventory_by_id(self,product_id):
        querry=f"SELECT products.product_id,products.product_name,category.category_name,products.quantity,products.price,products.images,vendors.vendor_name FROM products INNER JOIN vendors on products.vendor_id = vendors.vendor_id INNER JOIN category on products.category_id = category.category_id WHERE product_id = '{product_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def inventory_by_name(self,product_name):
        querry=f"SELECT products.product_id,products.product_name,category.category_name,products.quantity,products.price,products.images,vendors.vendor_name FROM products INNER JOIN vendors on products.vendor_id = vendors.vendor_id INNER JOIN category on products.category_id = category.category_id where product_name='{product_name}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def sort_inventory_id_desc(self):
        querry=f"SELECT * FROM inventory ORDER BY product_id DESC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def sort_inventory_id_asc(self):
        querry=f"SELECT * FROM inventory ORDER BY product_id ASC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def sort_inventory_name_asc(self):
        querry=f"SELECT * FROM inventory ORDER BY product_name ASC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def sort_inventory_name_desc(self):
        querry=f"SELECT * FROM inventory ORDER BY product_name DESC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def sort_inventory_quantity_asc(self):
        querry=f"SELECT * FROM inventory ORDER BY quantity ASC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def sort_inventory_quantity_desc(self):
        querry=f"SELECT * FROM inventory ORDER BY quantity DESC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def sort_inventory_price_asc(self):
        querry=f"SELECT * FROM inventory ORDER BY price ASC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def sort_inventory_price_desc(self):
        querry=f"SELECT * FROM inventory ORDER BY price DESC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def sort_user_name_asc(self):
        querry=f"SELECT * FROM customers ORDER BY user_name asc"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def sort_user_name_desc(self):
        querry=f"SELECT * FROM customers ORDER BY user_name DESC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def sort_user_num_asc(self):
        querry=f"SELECT * FROM customers ORDER BY phone_number ASC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def sort_user_num_desc(self):
        querry=f"SELECT * FROM customers ORDER BY phone_number DESC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def sort_user_mail_asc(self):
        querry=f"SELECT * FROM customers ORDER BY mail_id ASC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def sort_user_mail_desc(self):
        querry=f"SELECT * FROM customers ORDER BY mail_id DESC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def random_from_inventory(self):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result[1][0])
        return list(result)

    def cpu_page_items(self):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products where category_id='1'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return list(result)
    
    def headphone_page_items(self):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products where category_id='2'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return list(result)
    
    def keyboard_page_items(self):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products where category_id='3'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return list(result)
    
    def monitor_page_items(self):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products where category_id='4'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return list(result)
    
    def mouse_page_items(self):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products where category_id='5'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return list(result)
    
    def speaker_page_items(self):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products where category_id='6'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return list(result)

    def homepage_search(self,search):
        querry=f"SELECT images[1] product_brand,product_name,price,product_id FROM products WHERE product_name ILIKE '%{search}%' or product_description ILIKE '%{search}%' or product_brand ILIKE '%{search}%' " 
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def get_vendor_name(self,name):
        querry=f"SELECT * FROM vendors WHERE vendor_name='{name}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        return result

    def get_vendor_address(self,address):
        querry=f"SELECT * FROM vendors WHERE address='{address}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        return result

    def get_vendor_number(self,number):
        querry=f"SELECT * FROM vendors WHERE phone_number='{number}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        return result

    def get_vendor_mail(self,mail):
        querry=f"SELECT * FROM vendors WHERE mail_id='{mail}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        return result

    def vendor_add(self,name,address,number,mail):
        querry=f"INSERT INTO VENDORS (vendor_name,address,phone_number,mail_id) VALUES ('{name}','{address}','{number}','{mail}')"
        self.curr.execute(querry)
        self.conn.commit()

    def fetch_vendor(self):
        querry=f"SELECT * FROM vendors"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def vendor_search(self,search):
        querry=f"SELECT * FROM vendors WHERE vendor_name = '{search}' or address= '{search}' or mail_id ='{search}' or phone_number='{search}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result)
        return result

    def vendor_search_id(self,search):
        querry=f"SELECT * FROM vendors WHERE vendor_id='{search}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def vendor_delete(self,product_id):
        querry=f"DELETE FROM vendors WHERE vendor_id='{product_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def fetch_vendor_on_id(self,vendor_id):
        querry=f"SELECT * FROM vendors WHERE vendor_id='{vendor_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        return result

    def check_vendor_by_id(self,vendor_id):
        querry=f"SELECT * FROM vendors WHERE vendor_id='{vendor_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        if result:
            return "ok"
        else:
            return "no"
    
    def update_vendor_name(self,vendor_name,vendor_id):
        querry=f"UPDATE vendors SET vendor_name ='{vendor_name}' WHERE vendor_id='{vendor_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def check_vendor_name(self,vendor_name,vendor_id):
        querry=f"SELECT * FROM vendors where vendor_name='{vendor_name}' AND vendor_id!='{vendor_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        if result:
            return "yes"
        else:
            return "no"

    def check_vendor_address(self,address,vendor_id):
        querry=f"SELECT * FROM vendors where address='{address}' AND vendor_id!='{vendor_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        if result:
            return f"yes"
        else:
            return f"no"

    def check_vendor_number(self,number,vendor_id):
        querry=f"SELECT * FROM vendors where phone_number='{number}' AND vendor_id!='{vendor_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        if result:
            return "yes"
        else:
            return "no"

    def check_vendor_mail(self,mail_id,vendor_id):
        querry=f"SELECT * FROM vendors where mail_id='{mail_id}' AND vendor_id!='{vendor_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        if result:
            return "yes"
        else:
            return "no"

    def update_vendor_address(self,address,vendor_id):
        querry=f"UPDATE vendors SET address ='{address}' WHERE vendor_id='{vendor_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def update_vendor_number(self,number,vendor_id):
        querry=f"UPDATE vendors SET phone_number ='{number}' WHERE vendor_id='{vendor_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def update_vendor_mail_id(self,mail_id,vendor_id):
        querry=f"UPDATE vendors SET mail_id ='{mail_id}' WHERE vendor_id='{vendor_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def fetch_category(self):
        querry=f"SELECT * FROM category"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def category_by_id(self,search):
        querry=f"SELECT * FROM category WHERE category_id='{search}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result
    
    def category_by_name(self,search):
        querry=f"SELECT * FROM category WHERE category_name='{search}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def get_category(self,category_name):
        querry=f"SELECT * FROM category WHERE category_name='{category_name}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        if result:
            return "NO"
        else:
            return "YES"

    def add_category(self,category_name):
        querry=f"INSERT INTO category (category_name) VALUES ('{category_name}')"
        self.curr.execute(querry)
        self.conn.commit()

    def category_delete(self,category_id):
        querry=f"DELETE FROM category WHERE category_id ='{category_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def category_by_id(self,category_id):
        querry=f"SELECT * FROM category WHERE category_id='{category_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        # print(result[0][1])
        return result

    def category_edit(self,caGtegory_name,category_id):
        querry=f"UPDATE category SET category_name='{category_name}' WHERE category_id='{category_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def check_category(self,category_name,category_id):
        querry=f"SELECT * FROM category WHERE category_name='{category_name}' and category_id!='{category_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        if result:
            return "NO"
        else:
            return "YES"

    def get_vendor_id_name(self):
        querry=f"SELECT vendor_id,vendor_name FROM vendors"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def fetch_product_user(self,product_id):
        querry=f"SELECT product_brand,product_name,product_description,features,price,images FROM products WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def all_products(self):
        querry=f"SELECT * FROM products"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def cpu_brand_sort(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products where category_id='1' and product_brand='{sort}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result
    
    def headphone_brand_sort(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products where category_id='2' and product_brand='{sort}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result
 
    def keyboard_brand_sort(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products where category_id='3' and product_brand='{sort}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result
 
    def monitor_brand_sort(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products where category_id='4' and product_brand='{sort}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result
 
    def mouse_brand_sort(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products where category_id='5' and product_brand='{sort}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result
 
    def speaker_brand_sort(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products where category_id='6' and product_brand='{sort}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def cpu_price_asc(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id='1' ORDER BY price"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result
    
    def headphone_price_asc(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id='2' ORDER BY price"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result
    
    def keyboard_price_asc(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id='3' ORDER BY price"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result
    
    def monitor_price_asc(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id='4' ORDER BY price"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result
    
    def mouse_price_asc(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id='5' ORDER BY price"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result
   
    def speaker_price_asc(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id='6' ORDER BY price"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def cpu_price_desc(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id='1' ORDER BY price DESC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def headphone_price_desc(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id='2' ORDER BY price DESC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def keyboard_price_desc(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id='3' ORDER BY price DESC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def monitor_price_desc(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id='4' ORDER BY price DESC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def mouse_price_desc(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id='5' ORDER BY price DESC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def speaker_price_desc(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id='6' ORDER BY price DESC"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def cpu_all(self):
        querry=f"SELECT features FROM products WHERE category_id='1'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def headphone_all(self):
        querry=f"SELECT features FROM products WHERE category_id='2'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def keyboard_all(self):
        querry=f"SELECT features FROM products WHERE category_id='3'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def monitor_all(self):
        querry=f"SELECT features FROM products WHERE category_id='4'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def mouse_all(self):
        querry=f"SELECT features FROM products WHERE category_id='5'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def speaker_all(self):
        querry=f"SELECT features FROM products WHERE category_id='6'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def cpu_motherboard_sort(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id = 1 AND features::text LIKE '%{sort}%'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result
 
    def keyboard_sorting(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id = 3 AND features::text LIKE '%{sort}%'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def headphone_sorting(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id = 2 AND features::text LIKE '%{sort}%'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def monitor_sorting(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id = 4 AND features::text LIKE '%{sort}%'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def mouse_sorting(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id = 5 AND features::text LIKE '%{sort}%'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def speaker_sorting(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id = 6 AND features::text LIKE '%{sort}%'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def cpu_fan_sort(self,sort):
        querry=f"SELECT images[1],product_brand,product_name,price,product_id FROM products WHERE category_id = 1 AND features[2]::text LIKE '%{sort}%'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def get_price(self,product_id):
        querry=f"SELECT * FROM products WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        return result[5]

    def get_brand(self,product_id):
        querry=f"SELECT * FROM products WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        return result[2]

    def get_product_name(self,product_id):
        querry=f"SELECT * FROM products WHERE product_id='{product_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        return result[3]

    def add_cart(self,name,product_id,price,product_name,brand):
        querry=f"INSERT INTO cart (user_name,product_id,price,product_name,product_brand) VALUES ('{name}','{product_id}','{price}','{product_name}','{brand}')" 
        self.curr.execute(querry)
        self.conn.commit()

    def get_cart(self,name):
        querry=f"SELECT products.images[1],cart.* FROM cart INNER JOIN products ON cart.product_id=products.product_id WHERE cart.user_name='{name}' and cart.status='in_cart' ORDER BY cart.cart_id "
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def cart_count(self,name):
        querry=f"SELECT count(*) FROM cart WHERE user_name='{name}' AND status='in_cart'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        return result[0]

    def cart_product_id(self,name):
        querry=f"SELECT * FROM cart WHERE user_name='{name}' AND status='in_cart'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def cart_quantity(self,product_id):
        querry=f"SELECT * FROM cart WHERE product_id= '{product_id}' AND status='in_cart'"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        return result[2]

    def insert_in_check_out(self,product_id,name):
        querry=f"INSERT INTO check_out (product_id,user_name) VALUES ('{product_id}','{name}')"
        self.curr.execute(querry)
        self.conn.commit()

    def check_out_update_quantity(self,quantity,product_id):
        querry=f"UPDATE check_out SET quantity='{quantity}' WHERE product_id='{product_id}' AND payment = 'false'"
        self.curr.execute(querry)
        self.conn.commit()

    def check_out_update(self,customer_name,address,customer_number,payment_method,date_time,name):
        querry=f"UPDATE check_out set customer_name='{customer_name}',address='{address}',phone_number='{customer_number}',payment_method='{payment_method}',date_and_time='{date_time}',payment='in_progress' WHERE user_name = '{name}' and payment = 'false'"
        self.curr.execute(querry)
        self.conn.commit()

    def check_out_payment_update(self,name):
        querry=f"UPDATE check_out SET payment='done' where user_name='{name}' and payment='in_progress'"
        self.curr.execute(querry)
        self.conn.commit()

    def update_cart_status(self,name):
        querry=f"UPDATE cart SET status='purchased' WHERE user_name='{name}' AND status='in_cart'"
        self.curr.execute(querry)
        self.conn.commit()

    def update_quantity(self,cart_id,quantity):
        querry=f"UPDATE cart SET quantity='{quantity}' where cart_id='{cart_id}'"
        self.curr.execute(querry)
        self.conn.commit()

    def card_details(self,card_name,card_number):
        querry=f"INSERT INTO card_details (user_name,card_number) VALUES ('{card_name}','{card_number}')"
        self.curr.execute(querry)
        self.conn.commit()

    def check_out_details(self):
        querry=f"SELECT * FROM check_out"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def add_delivery_details(self,order_id,customer_name,user_name):
        querry=f"INSERT INTO delivery (order_id,customer_name,user_name) VALUES ('{order_id}','{customer_name}','{user_name}')"
        self.curr.execute(querry)
        self.conn.commit()

    def get_delivery_details(self):
        querry=f"SELECT * FROM delivery"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def join_delivery_product_category(self,name):
        querry=f"SELECT delivery.order_id,check_out.product_id,products.category_id,products.product_brand,products.product_name,products.images[1],check_out.date_and_time FROM delivery INNER JOIN check_out ON delivery.order_id=check_out.order_id INNER JOIN products ON check_out.product_id=products.product_id WHERE delivery.delivery_status='in_progress' and delivery.user_name='{name}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def check_out_using_order_id(self,order_id):
        querry=f"SELECT * FROM check_out WHERE order_id='{order_id}'"
        self.curr.execute(querry)
        result=self.curr.fetchall()
        return result

    def get_image_1(self,product_id):
        querry=f"SELECT images[1] FROM products WHERE product_id={product_id}"
        self.curr.execute(querry)
        result=self.curr.fetchone()
        return list(result)

    def delete_cart(self,cart_id):
        querry=f"UPDATE cart SET status='deleted' WHERE cart_id='{cart_id}'"
        self.curr.execute(querry)
        self.conn.commit()

# obj=UserDb()
# obj.join_delivery_product_category('Ninja')
