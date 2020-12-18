from types import MethodDescriptorType
from flask import Flask, render_template, request, redirect, abort
from login_app.login import User, login_check, register_check, lobby_check

app = Flask(__name__)

obj = User()

@app.route('/')
def index():
    return render_template('login_page.html')

@app.route('/homePage', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    result = obj.get_client(email)
    
    # login_check performs all of the operations needed.
    return login_check(password, result)


@app.route('/home', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    
    # register_check performs all of the operations needed for registration.
    return register_check(obj, email, password, confirm_password)

@app.route('/The_lobby', methods=['POST', 'GET'])
def lobby():
    if request.method == 'POST':
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
    return render_template('main_lobby.html')

if __name__ == "__main__":
    app.run(debug=True)
