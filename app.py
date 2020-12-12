from types import MethodDescriptorType
from flask import Flask, render_template, request, redirect, abort
from login_app.login import User

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
    
    if result:
        if result['Password'] == password:
            return render_template('index.html', username = result['User_name'])
        return abort(401, "Password entered is not correct")
    return abort(401, "Email Does Not exist")

@app.route('/home', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    
    if obj.check_client(email):
        return abort(400, "Email already exist")
    if password == confirm_password:
        username = obj.add_client(email, password, confirm_password)
        return render_template('index.html', username=username)
    return abort(400, "The Both password does not match")

@app.route('/lobby', methods=['POST'])
def lobby():
    email = obj.email
    TeamLead_username = request.form['TeamLead_username']
    TeamLead_profession = request.form['TeamLead_profession']
    Team_name = request.form['team_name']
    TeamMem_username = request.form.getlist('username')
    TeamMem_email = request.form.getlist('email')
    TeamMem_profession = request.form.getlist('profession')
    
    result = obj.get_client(email)
    if result['User_name'] != TeamLead_username:
        obj.update_client(email, {"$set": {'User_name': TeamLead_username}})
    obj.update_client(email, {"$set": {'TeamLead_profession': TeamLead_profession}})
    return TeamLead_profession

if __name__ == "__main__":
    app.run(debug=True)
