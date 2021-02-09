# Code for handling database for users that are logged in our site.
import pymongo
import datetime
from flask import render_template, abort, url_for, redirect, request, flash
from datetime import date, timedelta

client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')

mydb = client['Main_project']
information = mydb.theApp

class Tasker:
    '''
    Same as Node class
    '''
    def __init__(self, name, task = None) -> None:
        self.task = task
        self.name = name

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
    
    def set_team_name(self, team_name):
        self.team = mydb.Team
        self.team_name = team_name
    
    def access_team(self, team_name):
        return self.team.find_one({'team_name': team_name})
    
    def create_team(self, param):
        self.team_name = list(param.keys())[0]
        self.team.insert_one(param)
    
    def update_team(self, access_by, param):
        return self.team.update_one(access_by, param)
    
    def is_person_exist(self, team_name, person):
        team_data = self.access_team(team_name)
        members_name = team_data['members_name']
        leader_name = team_data['leader_name']
        
        if person in members_name:
            return True
        else:
            if person == leader_name:
                return True
            else:
                return False
    
    def team_progress(self):
        # today = self.today()
        team_name = self.team_name
        team_data = self.access_team(team_name)
        total_task = team_data.get('total_task', None)
        
        if not total_task:
            self.total_task = 0
        else:
            self.total_task = total_task['total_task']
    
    def task_done_progress(self):
        self.team_progress()
        total_task = self.total_task
        task_done = 2
        
        if total_task != 0:
            ratio = task_done/ total_task
            return ratio
        return 0
    
    def task_pending(self):
        total_task = 0
        task_done = 0
        
        pending = total_task - task_done
        
        if pending != 0:
            ratio = pending/ total_task
            return ratio
        return 0
    
    def today(self):
        return date.today().strftime("%b-%d-%Y")
    
    def date_task_tracker(self, team_name, task):
        today = self.today()
        db = self.access_team(team_name)
        today_check = db.get(today, None)
        
        if not today_check:
            data = {today: {'description': [task], 'total_task': 1}}
        else:
            ls = db[today]['description']
            ls.append(task)
            data = {today: {'description': ls, 'total_task': len(ls)}}
        
        self.update_team({'team_name': team_name}, {"$set": data})
    
    def today_task(self, date=None):
        """
        used to get total number of task for today or for the specific date entered.
        """
        if date is not None:
            today = date
        else:
            today = self.today()
        team_name = self.team_name
        team_data = self.access_team(team_name)
        today_data = team_data.get(today, None)
        
        if not today_data:
            return 0
        else:
            return today_data['total_task']
    
    def today_perform(self):
        '''
        this function is used to find today's performance of the team;
        comparing today with yesterday and providing performance accordingly.
        '''
        today = date.today()
        yesterday = (today - timedelta(days=1)).strftime("%b-%d-%Y")
        today_task_num = self.today_task()
        yesterday_task_num = self.today_task(yesterday)
        
        diff = yesterday_task_num - today_task_num
        total = yesterday_task_num + today_task_num
        
        if diff < 0:
            # performance increased
            diff = -diff
            res = (diff / total) * 100
            ans = 'Increased'
        
        elif diff > 0:
            # performance decreased
            res = (diff / total) * 100
            ans = 'Decreased'
        
        else:
            # performance same as previous
            res = 0
            ans = 'Neutral'
        
        return (res, ans)
    
    def getAllDetails(self):
        team_name = self.team_name
        team_data = self.access_team(team_name)
        members = team_data.get('members_name', None)
        
        # Creating an empty list used to store name and the task for each person
        ls = []
        
        # Adding members and their task into the list
        if members is not None:
            
            # fetching members list in the database
            for member in members:
                member_detail = team_data.get(member, None)
                
                # getting further details for the particular member if exists
                if member_detail is not None:
                    for tasks in member_detail['description']:
                        
                        # Creating a Node and appending it into the list
                        tasker = Tasker(member, tasks)
                        ls.append(tasker)
        
        # getting leader's name and further details
        leader = team_data['leader_name']
        leader_detail = team_data.get(leader, None)
        
        # if any task is assigned to the leader then it must be appended into the list
        if leader_detail is not None:
            for tasks in leader_detail['description']:
                
                # Creating a Node and appending it into the list
                tasker = Tasker(leader, tasks)
                ls.append(tasker)
        
        return ls


def part_of_homepage(result):
    if result['team_status']:
        choice_value = True
        team_number = result['team_number']
        team_name_ls = [result[str(i)]['Team_name']
                                    for i in range(1, team_number + 1)]
    else:
        choice_value = False
        team_number = -1
        team_name_ls = []
        
    return render_template('index.html',
                        username=result['User_name'],
                        choice=choice_value,
                        team_number = team_number,
                        team_name_ls = team_name_ls,
                        email=result['Email'],
                        )

def login_check(password, result):
    if result:
        if result['Password'] == password:
            return part_of_homepage(result)
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
    obj.create_team({'team_name': Team_name, 'members_name': TeamMem_username, 'leader_name': TeamLead_username})
    
    # flash("Team Created Successfully!")
    
    flash('Created Team Successfully', 'succes')
    
    return redirect(url_for('login'))

    # return redirect(request.url)

def total_task_assigner(obj, team_name, task_description):
    main_data = obj.access_team(team_name)
    get_total_task = main_data.get('total_task', None)
    
    if not get_total_task:
        data = {'total_task': {'description': [task_description], 'total_task': 1}}
    else:
        ls = get_total_task['description']
        ls.append(task_description)
        total_task_length = len(ls)
        data = {'total_task': {'description': ls, 'total_task': total_task_length}}
    
    obj.update_team({'team_name': team_name}, {"$set": data})

def task_assigner(obj, team_name, task_description, person):
    data = obj.access_team(team_name)
    person_exist = obj.is_person_exist(team_name, person)
    
    if person_exist:
        get_person = data.get(person, None)
        
        if not get_person:
            set_task = {person : {"description": [task_description], 'total_task': 1}}
        else:
            ls = get_person['description']
            ls.append(task_description)
            total_task_length = len(ls)
            set_task = {person: {"description": ls, 'total_task': total_task_length}}
            
        obj.update_team({'team_name': team_name}, {"$set": set_task})
        
    else:
        print("Person is not in your team!!")
