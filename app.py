from types import MethodDescriptorType
from flask import Flask, render_template, request, redirect, abort
from login_app.login import User, login_check, register_check

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
    
    return register_check(obj, email, password, confirm_password)

@app.route('/lobby', methods=['POST'])
def lobby():
    email = obj.email
    TeamLead_username = request.form['TeamLead_username']
    TeamLead_profession = request.form['TeamLead_profession']
    Team_name = request.form['team_name']
    TeamMem_username = request.form.getlist('username')
    TeamMem_email = request.form.getlist('email')
    TeamMem_profession = request.form.getlist('profession')
    
    result = obj.get_client(email, False)
    if result['User_name'] != TeamLead_username:
        # update the username if the team lead changed that.
        obj.update_client(email, {"$set": {'User_name': TeamLead_username}})
    
    # update the profession of team leader.
    obj.update_client(email, {"$set": {'TeamLead_profession': TeamLead_profession}})
    
    if result['team_status'] == True:
        updated_team_number = result['team_number'] + 1
        obj.update_client(email, {"$set": {'team_number': updated_team_number}})
    else:
        updated_team_number = 0
        obj.update_client(email, {"$set": {'team_status': True}})
        obj.update_client(email, {"$set": {'team_number': updated_team_number}})
    
    # Updating the creadentials for team members:-
    count_ls = [i for i in range(1, len(TeamMem_profession) + 1)]
    iterable_item = zip(count_ls, TeamMem_username, TeamMem_email, TeamMem_profession)
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

if __name__ == "__main__":
    app.run(debug=True)
