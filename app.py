# Jared Tauler, Max McLaughlin (has done NOTHING because jackson and richard distracted him)
# 5/5/21
# 1st version of Ticket System

# pip install mysqlclient, redis, cryptography
# or you will crash.

from flask import Flask, render_template, request, redirect, url_for, session,
from flask_session.__init__ import Session
from flask.socketio import SocketIO, emit
# from flask_sqlalchemy import SQLalchemy

import pandas as pd

# MySQL
import pymysql
from sqlalchemy import create_engine

import os
import hashlib

def ConnectionString(USERNAME, PASS, HOST):
    DBstr = "mysql+pymysql://" \
            + USERNAME + \
            ":" \
            + PASS + \
            "@" \
            + HOST
    return DBstr


# Execute to DB
def ExecuteDB(cmd, engine, returning=False):
    print(f"Executing to DB {cmd}")
    with engine.connect() as connection:
        curr = connection.execute(cmd)

    if returning:
        result = curr.fetchall()
        print(f"Result was {result}")
        return result


# Custom exceptions.
class TicketSystemError(Exception): pass
class BadInputError(TicketSystemError): pass
class DatabaseError(TicketSystemError): pass

## Main program
app = Flask(__name__)
app.config["SECRET_KEY"] = "211910"
# print(ConnectionString("jlt", "1234", "localhost"))

# Connect to DB server
engine = create_engine(ConnectionString("jlt", "1234", "localhost"))  # pip install mysqlclient

# a = pd.read_sql_table("user", con=DB, schema="ticketsystem")
# SESSION_TYPE = 'redis'
# app.config.from_object(__name__)
# Session(app)
#
# @app.route('/set/')
# def set():
#     session['key'] = 'value'
#     return 'ok'
# #
# @app.route('/get/')
# def get():
#     return session.get('key', 'not set')
# sess = Session()
# sess.init_app(app)
# print(sess)

@app.route('/login', methods=["GET", "POST"])
def Login():
    print(request.method)
    session.clear()
    if request.method == "POST":
        if request.form.get('login'):
            username = request.form.get("username")
            password = request.form.get("password")
            form = {}
            for i in ["password", "username"]:
                form[i] = request.form.get(i)

            user = pd.read_sql_query(f"SELECT * FROM `ticketsystem`.`user` WHERE `username` LIKE '{form['username']}'", engine)
            if user.empty:
                raise DatabaseError("User not in Database")

            password = bytes.fromhex(user["password"].values[0])
            salt = bytes.fromhex(user["salt"].values[0])

            hashed = hashlib.pbkdf2_hmac('sha256',form["password"].encode('utf-8'), salt, 100000)

            if hashed != password:
                return "Bad password!"

            session["user"] = user["username"].values[0]
            session["email"] = user["email"].values[0]
            print(session)
            return redirect(url_for("Home"))
        elif request.form.get('signup'): return redirect(url_for("Signup"))

    return render_template("login.html")


@app.route("/")
def Home():
    if "user" in session:
        return render_template("home.html")
    else:
        return redirect(url_for("Login")) # Redirect back to login if no user.


@app.route("/signup", methods=["GET", "POST"])
def Signup():
    if request.method == "POST":

        form = {}
        for i in ["password", "confirmpassword", "username", "email"]:
            form[i] = request.form.get(i)
        try:
            # TODO Do all checks that don't require connecting to the database in the HTML with scripts.
            for i in ["password", "username", "email"]:
                # Check for blank or only space characters
                if form[i].isspace() or form[i] == "":
                    raise BadInputError(f"Your {i.capitalize()} cannot be blank.")
                # Check for space characters
                if form[i].find(" ") != -1:
                    raise BadInputError(f"Your {i.capitalize()} cannot have spaces.")

            # Check password
            if form["password"] != form["confirmpassword"]:
                raise BadInputError("Passwords do not match.")

            # Check if username is taken. SQL command will return rows with matching username. (which will never be more than 1)
            if len(ExecuteDB(f"SELECT * FROM `ticketsystem`.`user` WHERE `username` LIKE '{form['username']}'", engine, True)) > 0:
                raise DatabaseError(f"The username {form['username']} is already taken.")

            salt = os.urandom(32)  # Remember this
            hashed = hashlib.pbkdf2_hmac('sha256', form["password"].encode('utf-8'), salt, 100000)

            # Store hashed and salt as hex in the database.
            ExecuteDB(
                f"INSERT INTO `ticketsystem`.`user` (`username`, `email`, `password`, `salt`) VALUES \
                ('{form['username']}', '{form['email']}', '{hashed.hex()}', '{salt.hex()}')"
            , engine)

            return redirect(url_for("Login"))

        except Exception as E:
            return render_template("signup.html", error=E)


    return render_template("signup.html")

if __name__ == '__main__':
    app.run(debug=True)

