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
                team_number = result['team_number']
                team_name_ls = [result[str(i)]['Team_name'] for i in range(1, team_number + 1)]
            else:
                choice_value = False
                team_number = -1
                team_name_ls = []
                
            return render_template('index.html',
                                username=result['User_name'],
                                choice=choice_value,
                                team_number = team_number,
                                team_name_ls = team_name_ls,
                                )
        return abort(401, "Password entered is not correct")
    return abort(401, "Email Does Not exist")

def register_check(obj, email, password, confirm_password):
    if obj.check_client({'Email': email}):
        return abort(400, "Email already exist")
    if password == confirm_password:
        username = obj.add_client(email, password, confirm_password)
        return render_template('index.html', username=username)
    return abort(400, "The Both password does not match")

def lobby_check(obj, result, email, context):
    TeamLead_username = context.get("TeamLead_username")
    TeamLead_profession = context.get("TeamLead_profession")
    Team_name = context.get("Team_name")
    TeamMem_username = context.get("TeamMem_username")
    TeamMem_email = context.get("TeamMem_email")
    TeamMem_profession = context.get("TeamMem_profession")
    
    if result['User_name'] != TeamLead_username:
        # update the username if the team lead changed that.
        obj.update_client(email, {"$set": {'User_name': TeamLead_username}})

    # update the profession of team leader.
    obj.update_client(
        email, {"$set": {'TeamLead_profession': TeamLead_profession}})

    if result['team_status'] == True:
        updated_team_number = result['team_number'] + 1
        obj.update_client(
            email, {"$set": {'team_number': updated_team_number}})
    else:
        updated_team_number = 1
        obj.update_client(email, {"$set": {'team_status': True}})
        obj.update_client(
            email, {"$set": {'team_number': updated_team_number}})

    # Updating the creadentials for team members:-
    count_ls = [i for i in range(1, len(TeamMem_profession) + 1)]
    iterable_item = zip(count_ls, TeamMem_username,
                        TeamMem_email, TeamMem_profession)
    team_member_dict = {}

    for counter, username, useremail, profession in iterable_item:
        member = "TeamMember_" + str(counter)
        # member_details = {member: {"User_name": username, "Email": useremail, "profession": profession}}
        team_member_dict[member] = {
            "User_name": username, "Email": useremail, "profession": profession}

    updated_team_detail = {str(updated_team_number): {
        "Team_members_details": team_member_dict, 'Team_name': Team_name}}
    obj.update_client(email, {"$set": updated_team_detail})

    # Create another collection for teams
    obj.team_creation()
    obj.create_team({Team_name: team_member_dict})

    return TeamLead_profession
