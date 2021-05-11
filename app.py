# Jared Tauler, Max McLaughlin (has done NOTHING because jackson and richard distracted him)
# 5/5/21
# 1st version of Ticket System

# pip install mysqlclient, redis, cryptography
# or you will crash.
import base64

from flask import Flask, render_template, request, redirect, url_for, session
from flask_session.__init__ import Session
# from flask_sqlalchemy import SQLalchemy

import pandas as pd

# MySQL
import pymysql
from sqlalchemy import create_engine

import os
import hashlib
import io


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
class DatabaseConflict(TicketSystemError): pass

## Main program
app = Flask(__name__)
app.config["SECRET_KEY"] = "211910"
# print(ConnectionString("jlt", "1234", "localhost"))

# Connect to DB server
engine = create_engine(ConnectionString("jlt", "1234", "192.168.0.131"))  # pip install mysqlclient

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

@app.route('/', methods=["GET", "POST"])
def Login():
    print(request.method)
    if request.method == "POST":
        if request.form.get('login'):
            # getting input with name = fname in HTML form
            username = request.form.get("username")
            # getting input with name = lname in HTML form
            password = request.form.get("password")
            # password = 'password123'
            #
            #
            # password_to_check = 'password123' # The password provided by the user to check
            #
            # # Use the exact same setup you used to generate the key, but this time put in the password to check
            # new_key = hashlib.pbkdf2_hmac(
            #     'sha256',
            #     password_to_check.encode('utf-8'), # Convert the password to bytes
            #     salt,
            #     100000
            # )
            #
            # if new_key == key:
            #     print('Password is correct')
            # else:
            #     print('Password is incorrect')
            session["user"] = "21"
            return redirect(url_for("Home"))
        elif request.form.get('signup'): return redirect(url_for("Signup"))

    return render_template("login.html")


@app.route("/home")
def Home():
    if "user" in session:
        return "home"
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
            if len(ExecuteDB(f"SELECT * FROM ticketsystem.user WHERE `username` LIKE '{form['username']}'", engine, True)) > 0:
                raise DatabaseConflict(f"The username {form['username']} is already taken.")

            salt = os.urandom(32)  # Remember this
            hashed = hashlib.pbkdf2_hmac('sha256', form["password"].encode('utf-8'), salt, 100000)

            # Store hashed and salt as hex in the database.
            ExecuteDB(
                f"INSERT INTO `ticketsystem`.`user` (`username`, `email`, `password`, `salt`) VALUES \
                ('{form['username']}', '{form['email']}', '{hashed.hex()}', '{salt.hex()}')"
            , engine)


        except Exception as e:
            return str(e)


    return render_template("signup.html")

if __name__ == '__main__':
    app.run(debug=True)

