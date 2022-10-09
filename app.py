from flask import Flask

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
import sqlite3

# Configures application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Connects to SQLite Database to store account information TODO: create table that stores pairings
con = sqlite3.connect("accountability.db", check_same_thread=False)
cur = con.cursor()

# User
curr_user = ""

@app.route("/")
def index():
    return render_template('index.html', curr_user=curr_user)

@app.route("/about")
def about():
    return render_template('about.html', curr_user=curr_user)

@app.route("/how-it-works")
def getting_started():
    return render_template('how-it-works.html', curr_user=curr_user)

@app.route("/logout")
def logout():
    global curr_user
    curr_user = ""
    return render_template('index.html', curr_user=curr_user)

# Login TODO: If have time, SHA 256 hash for security
@app.route("/login", methods=["GET", "POST"])
def login():
    global curr_user
    if request.method == "GET":
        return render_template('login.html', curr_user="")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

        real_password = cur.execute("""SELECT password FROM accounts WHERE name=?""", (username,))
        real_password = cur.fetchone()

        if not real_password:
            return render_template('login.html', error="Username doesn't exist!", curr_user=curr_user)
        elif real_password[0] != password:
            return render_template('login.html', error="Wrong password!", curr_user=curr_user)
        else:
            curr_user = username
            return render_template('index.html', curr_user=curr_user)

# Create Account
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if curr_user == "":
            return render_template('register.html', curr_user=curr_user)
        else:
            return render_template('find-topics.html', curr_user=curr_user)
    else:
        # Gets information inputted
        username = request.form.get("username")
        email = request.form.get("email").lower()
        password = request.form.get("password")
        
        if not username or not email or not password:
            return render_template('register.html', error="Error: Fill out every field!", curr_user=curr_user)

        # Check if username already exists
        existing_usernames = cur.execute("""SELECT name FROM accounts""")
        existing_usernames = cur.fetchall()
        for e_username in existing_usernames:
            if e_username[0] == username:
                return render_template('register.html', error="Error: Username already exists!", curr_user=curr_user)

        # Check if email already exists
        existing_emails = cur.execute("""SELECT email FROM accounts""")
        existing_emails = cur.fetchall()
        for e_email in existing_emails:
            if e_email[0] == email:
                return render_template('register.html', error="Error: Email already exists!", curr_user=curr_user)

        # Insert account information into database
        cur.execute("""INSERT INTO accounts VALUES (?, ?, ?)""", (username, password, email))
        con.commit()

        return render_template('index.html', curr_user=curr_user)