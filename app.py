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
            return render_template('index.html')
        return abort(401, "Password entered is not correct")
    return abort(401, "Email Does Not exist")

@app.route('/home', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    
    if password == confirm_password:
        obj.add_client(email, password, confirm_password)
        return render_template('index.html', confirmPassword = confirm_password)
    return abort(400, "The Both password does not match")


if __name__ == "__main__":
    app.run(debug=True)
