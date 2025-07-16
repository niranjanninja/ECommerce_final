import psycopg2
# from read_text_file import read_file,read_psy
from configparser import ConfigParser
file='/home/ubuntu/projectsql/login_page/libs/config.ini'
config=ConfigParser()
config.read(file)

class DBConnect:
    def __init__(self, database: str = 'Customers'):
        # text=read_file('./libs/connection_details.txt')
        # return text
        self.database =  database
        self.user = config['DB_details']['user']
        self.password = config['DB_details']['password']
        self.host = config['DB_details']['host']
        self.port = config['DB_details']['port']

    def connect_to_db(self):
        # This method returns the connection object
        connect_obj = psycopg2.connect(database=self.database,user=self.user, password=self.password, host=self.host,port=self.port)
        return connect_obj

    def check_db_connection(self) -> dict:
        connection_obj = self.connect_to_db()
        if connection_obj:
            return {'data': connection_obj, 'status': True, 'message': "Db connection successfully"}
            # print("Connected")
        else:
            return {'data': None, 'status': False, 'message': "Db connection failed"}
            # print("Failed")

# obj=DBConnect()
# obj.check_db_connection()

