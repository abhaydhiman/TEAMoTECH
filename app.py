import os
from flask import Flask, render_template, request, redirect, abort, session
from login_app.login import User, login_check, register_check, lobby_check, part_of_homepage

app = Flask(__name__)

app.secret_key = os.urandom(24)

obj = User()

@app.route('/')
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
    email = obj.email
    TeamLead_username = request.form['TeamLead_username']
    TeamLead_profession = request.form['TeamLead_profession']
    Team_name = request.form['team_name']
    # team_name = Team_name
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

@app.route('/main_lobby', methods=['POST'])
def main_lobby():
    team_name = request.form['team_name']
    return f"hello {team_name}"


if __name__ == "__main__":
    app.run(debug=True)
