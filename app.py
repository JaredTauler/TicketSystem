# Jared Tauler, Max McLaughlin (has done NOTHING because jackson and richard distracted him)
# 5/5/21
# 1st version of Ticket System

# pip install mysqlclient, redis, cryptography, simple-websocket

from flask import Flask, render_template, request, redirect, url_for, session
from flask_session.__init__ import Session
import flask_socketio as io
from flask_socketio import send, emit
# from flask_sqlalchemy import SQLalchemy

import eventlet

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
app.config["SECRET_KEY"] = "21"
socketio = io.SocketIO(app)
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
    # print(request.method)
    print("21")
    session.clear()
    return render_template("login.html")

@socketio.event
def LoginIO(data):
    print(data)

    # if request.method == "POST":
    #     if request.form.get('login'):
    #         username = request.form.get("username")
    #         password = request.form.get("password")
    #         form = {}
    #         for i in ["password", "username"]:
    #             form[i] = request.form.get(i)
    #
    #         user = pd.read_sql_query(f"SELECT * FROM `ticketsystem`.`user` WHERE `username` LIKE '{form['username']}'", engine)
    #         if user.empty:
    #             raise DatabaseError("User not in Database")
    #
    #         password = bytes.fromhex(user["password"].values[0])
    #         salt = bytes.fromhex(user["salt"].values[0])
    #
    #         hashed = hashlib.pbkdf2_hmac('sha256',form["password"].encode('utf-8'), salt, 100000)
    #
    #         if hashed != password:
    #             return "Bad password!"
    #
    #         session["user"] = user["username"].values[0]
    #         session["email"] = user["email"].values[0]
    #         print(session)
    #         return redirect(url_for("Home"))
    #     elif request.form.get('signup'): return redirect(url_for("Signup"))



@app.route("/")
def Home():
    if "user" in session:
        return render_template("home.html")
    else:
        return redirect(url_for("Login")) # Redirect back to login if no user.


@app.route("/signup", methods=["GET", "POST"])
def Signup(): return render_template("signup.html")

# Script for sign up
@socketio.event
def SignupSubmit(form):
    problem = []
    if form["password"] != form["confirmpassword"]:
        problem.append("Passwords do not match.")

    for i in ["password", "username", "email"]:
        # Check for blank or only space characters
        if form[i].isspace() or form[i] == "":
            problem.append(f"Your {i.capitalize()} cannot be blank.")
        # Check for space characters
        if form[i].find(" ") != -1:
            problem.append(f"Your {i.capitalize()} cannot have spaces.")

    # Check if user is already in database or not. Length will be more than 0 if user is already present.
    if len(
        ExecuteDB(f"SELECT * FROM `ticketsystem`.`user` WHERE `username` LIKE '{form['username']}'", engine, True)
    ) > 0:
        problem.append(f"The username {form['username']} is already taken.")

    if problem != []: io.emit('problem', problem)
    else:
        # password hashing
        salt = os.urandom(32)
        hashed = hashlib.pbkdf2_hmac('sha256', form["password"].encode('utf-8'), salt, 100000)

        # Store hashed and salt as hex in the database.
        ExecuteDB(
            f"INSERT INTO `ticketsystem`.`user` (`username`, `email`, `password`, `salt`) VALUES \
            ('{form['username']}', '{form['email']}', '{hashed.hex()}', '{salt.hex()}')"
            , engine)

        # redirect after succesfully signing up
        io.emit('redirect', url_for("Login"))


if __name__ == '__main__':
    socketio.run(app, debug=False)

