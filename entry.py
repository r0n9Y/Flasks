from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from settings import *

app = Flask(__name__)
app.secret_key = "KeyForSession"
app.permanent_session_lifetime = timedelta(minutes = 10)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(128))
    email = db.Column("email", db.String(128), unique=True)

    def __init__(self, name, email):
        self.name = name
        self.email = email

@app.route("/")
def home():
    return render_template("index.html")

@app.route(f"/{PAGE_LOGIN}", methods=["POST","GET"])
def login():
    if request.method == "POST":
        session.permanent_session_lifetime = True
        userName = request.form["field_name"]
        session[SESSION_KEY_USER] = userName
        print(f"session {SESSION_KEY_USER}: {session[SESSION_KEY_USER]}")
        flash(f"> {session[SESSION_KEY_USER]} is logged in successfully <", "info")

        # store the logged in user table
        foundUser = users.query.filter_by(name = userName).first()
        if foundUser:
            session[SESSION_KEY_EMAIL] = foundUser.email
        else:
            newUser = users(userName, "")
            db.session.add(newUser)
            db.session.commit()
        return redirect(url_for(PAGE_WELCOME))
    else:
        if SESSION_KEY_USER in session:
            flash("> Already logged in <", "info")
            return redirect(url_for(PAGE_WELCOME))
        else:
            return render_template("login.html")

@app.route(f"/{PAGE_WELCOME}", methods=["POST", "GET"])
def welcome():
    str_email = None
    if SESSION_KEY_USER in session:
        if  "POST" == request.method:
            flash("> The user email is saved into the session <", "info")
            str_email = request.form["mail"]
            session[SESSION_KEY_EMAIL] = str_email

            # Stores the user's email
            foundUser = users.query.filter_by(name=session[SESSION_KEY_USER]).first()
            if foundUser:
                foundUser.email = str_email
                db.session.commit()
        else:
            if SESSION_KEY_EMAIL in session:
                str_email = session[SESSION_KEY_EMAIL]
        return render_template("welcome.html", str_email = str_email)
    # if a accessor has not logged in, put the accessor to login page 
    else:
        flash("> Please log in <")
        return redirect(url_for(PAGE_LOGIN))

@app.route(f"/{PAGE_LOGOUT}")
def logout():
    if SESSION_KEY_USER in session:
        flash(f"> {session[SESSION_KEY_USER]} is logged out, have a nice day <", "info")
        session.pop(SESSION_KEY_USER, None)
        session.pop(SESSION_KEY_EMAIL, None)
    
    return redirect(url_for(PAGE_LOGIN))

if __name__ == "__main__":
    # Make sure the database is created before the app is started to run
    db.create_all()
    # debug=True : not need to ctrl-C to stop server and re-run
    app.run(debug=True)
