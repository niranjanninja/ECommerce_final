import psycopg2
import os
from configparser import ConfigParser
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(BASE_DIR, "config.ini")
config=ConfigParser()
config.read(file)

class DBConnect:
    def __init__(self, database: str = 'Customers'):
        self.database =  database
        self.user = config['DB_details']['user']
        self.password = config['DB_details']['password']
        self.host = config['DB_details']['host']
        self.port = config['DB_details']['port']

    def connect_to_db(self):
        connect_obj = psycopg2.connect(database=self.database,user=self.user, password=self.password, host=self.host,port=self.port)
        return connect_obj

    def check_db_connection(self) -> dict:
        connection_obj = self.connect_to_db()
        if connection_obj:
            return {'data': connection_obj, 'status': True, 'message': "Db connection successfully"}
        else:
            return {'data': None, 'status': False, 'message': "Db connection failed"}

# obj=DBConnect()
# obj.check_db_connection()

