from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = os.urandom(32)
engine = create_engine("postgresql://postgres:omaralany@localhost/login")
db = scoped_session(sessionmaker(bind=engine))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    msg = ""
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        account = db.execute('SELECT * FROM users WHERE email = :email AND password = :password', {"email":email, "password":password,}).fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            session['name'] = account['name']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('login'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    msg = ""
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'password' in request.form and 'confirm' in request.form:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']
        account = db.execute('SELECT * FROM users WHERE email = :email',{'email':email,}).fetchone()
        if account:
            msg = "The account already exists"
        elif name == "" or email == "" or password == "" or confirm == "":
            msg = "Make sure to enter all the information"
        elif password != confirm:
            msg = "The password and confirm password not match"
        elif len(name) < 5 or len(name) > 20:
            msg = "Username most be more then 5 lenght and less the 20 lenght"
        elif len(password) < 5:
            msg = "Password most be more then 5 lenght"
        else:
            db.execute('INSERT INTO users(name, email, password) VALUES(:name, :email, :password)', {'name':name, 'password':password, 'email':email})
            db.commit()
            return render_template("gologin.html")
    return render_template("register.html", msg=msg)

@app.route("/")
def home():
    if 'loggedin' in session:
        account = db.execute('SELECT * FROM users WHERE id = :id',{'id':session['id'],}).fetchone()
        return render_template('home.html', account=account)
    return redirect(url_for('login'))
if __name__ == "__main__":
    app.run()