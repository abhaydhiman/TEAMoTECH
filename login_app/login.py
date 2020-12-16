# Code for handling database for users that are logged in our site.

import pymongo
import datetime
from flask import render_template, abort

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
            'team_status': False,
        })
        return username
    
    def check_client(self, param):
        if information.find_one(param):
            return True
        else:
            return False
    
    def get_client(self, email, update_login=True):
        self.email = email
        if update_login:
            self.update_client(email, {"$set": {'LoginDate': self.current_date}})
        return information.find_one({'Email': email})
    
    def update_client(self, email, params):
        return information.update_one({'Email': email}, params)
    
    def team_creation(self):
        self.team = mydb.Team
    
    def access_team(self, team_name):
        return self.team.find_one(team_name)
    
    def create_team(self, param):
        self.team.insert_one(param)
    
    def update_team(self, access_by, param):
        return self.team.update_one(access_by, param)

def login_check(password, result):
    if result:
        if result['Password'] == password:
            if result['team_status']:
                choice_value = True
            else:
                choice_value = False
            return render_template('index.html', username=result['User_name'], choice=choice_value)
        return abort(401, "Password entered is not correct")
    return abort(401, "Email Does Not exist")

def register_check(obj, email, password, confirm_password):
    if obj.check_client({'Email': email}):
        return abort(400, "Email already exist")
    if password == confirm_password:
        username = obj.add_client(email, password, confirm_password)
        return render_template('index.html', username=username)
    return abort(400, "The Both password does not match")
