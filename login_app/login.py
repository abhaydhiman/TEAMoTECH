# Code for handling database for users that are logged in our site.

import pymongo

client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')

mydb = client['Main_project']
information = mydb.theApp

class User:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def add_client(email, password, confirm_password):
        username = email.split('@')[0]
        information.insert_one({
            'User_name': username,
            'Email': email,
            'Password': password,
            'ConfirmPassword': confirm_password,
        })
    
    def get_client(self, email):
        return information.find_one({'Email': email})