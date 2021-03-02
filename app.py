import json
from flask import Flask, render_template, request, session
from login_app.login import User, login_check, register_check, lobby_check, part_of_homepage, task_assigner, total_task_assigner, removeTask

app = Flask(__name__)

# app.secret_key = os.urandom(24)

obj = User()

class Caller:
    def for_main_lobby(self, team_name):
        obj.set_team_name(team_name)
        email = obj.email
        data = obj.get_client(email, False)
        username = data['User_name']
        profession = data['TeamLead_profession']
        whole_progress = obj.task_done_progress()
        total_task_num = obj.total_task
        today_task_num = obj.today_task()
        card_1_data = obj.today_perform()
        task_details = obj.getAllDetails()
        report_details = obj.getReportDetails()
        pending_task_num = obj.getPendingTask()
        sec_card_data = obj.sec_card_data()
        data_seven_days = obj.prevSevDays()
        print(data_seven_days)
        
        return {'team_name': team_name, 'username': username,
                'profession': profession, 'whole_progress': whole_progress,'total_task_num': total_task_num, 'today_task_num': today_task_num, 'card_1_data': card_1_data, 'task_details': task_details,
                'report_details': report_details, 'pending_task_num': pending_task_num, 'sec_card_data': sec_card_data, 'seven_days': data_seven_days,
                }
    
    def for_assign_task(self):
        task_description = request.args.get('task_description')
        assign_to = request.args.get('assign_to')
        deadline = request.args.get('deadline')
        team_name = obj.team_name
        is_person_exist = obj.is_person_exist(team_name, assign_to)
        
        if deadline == '':
            deadline = None
        
        if is_person_exist:
            obj.date_task_tracker(team_name, task_description)
            task_assigner(obj, team_name, task_description, assign_to, deadline)
            total_task_assigner(obj, team_name, task_description)
        
        context = self.for_main_lobby(team_name)
        return render_template('main_lobby.html', context=context)
    
    def for_lobby(self):
        email = obj.email
        TeamLead_username = request.form['TeamLead_username']
        TeamLead_profession = request.form['TeamLead_profession']
        Team_name = request.form['team_name']
        TeamMem_username = request.form.getlist('username')
        TeamMem_email = request.form.getlist('email')
        TeamMem_profession = request.form.getlist('profession')
        
        result = obj.get_client(email, False)
        context = {
            "TeamLead_username": TeamLead_username,
            "TeamLead_profession": TeamLead_profession,
            "Team_name": Team_name,
            "TeamMem_username": TeamMem_username,
            "TeamMem_email": TeamMem_email,
            "TeamMem_profession": TeamMem_profession,
        }
        
        return lobby_check(obj, result, email, context)
    
    def for_task_done(self, team_name, data):
        name = data.get('name')
        task = data.get('task')
        removeTask(team_name, name, task)
        context = self.for_main_lobby(team_name)
        return context


@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('login_page.html')

@app.route('/homePage', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        session['email'] = email
        password = request.form['password']
        result = obj.get_client(email)
        
        # login_check performs all of the operations needed.
        return login_check(password, result)
    else:
        email = obj.email
        result = obj.get_client(email, False)
        return part_of_homepage(result)


@app.route('/home', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    
    # register_check performs all of the operations needed for registration.
    return register_check(obj, email, password, confirm_password)

@app.route('/The_lobby', methods=['POST'])
def lobby():
    caller = Caller().for_lobby()
    return caller

@app.route('/main_lobby', methods=['POST'])
def main_lobby():
    team_name = request.form['team_name']
    caller = Caller()
    context = caller.for_main_lobby(team_name)
    return render_template('main_lobby.html', context=context)


@app.route('/assign_task', methods=['POST', 'GET'])
def assign_task():
    caller = Caller().for_assign_task()
    return caller


@app.route('/task_done', methods=['POST', 'GET'])
def taskDone():
    data = json.loads(request.args.get('jsdata'))
    team_name = obj.team_name
    caller = Caller()
    context = caller.for_task_done(team_name, data)
    return render_template('main_lobby.html', context=context)

if __name__ == "__main__":
    app.run(debug=False)
