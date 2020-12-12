# Code for handling database for users that are logged in our site.

import pymongo
import datetime
client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')

mydb = client['Main_project']
information = mydb.theApp

class User:
    def __init__(self) -> None:
        self.current_date = datetime.datetime.today().strftime('%d-%b-%Y')
    
    def add_client(self, email, password, confirm_password):
        username = email.split('@')[0]
        self.email = email
        
        information.insert_one({
            'User_name': username,
            'Email': email,
            'Password': password,
            'ConfirmPassword': confirm_password,
            'LoginDate': self.current_date,
            'AccountCreated': self.current_date,
        })
        return username
    
    def check_client(self, email):
        try:
            information.find_one({'Email':email})
            return True
        except:
            return False
    
    def get_client(self, email):
        self.email = email
        self.update_client(email, {"$set": {'LoginDate': self.current_date}})
        return information.find_one({'Email': email})
    
    def update_client(self, email, params):
        return information.update_one({'Email': email}, params)
