from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

# MySQL
import pymysql
from sqlalchemy import create_engine
import cryptography

# Passwords
import hashlib
import os

salt = os.urandom(32) # Remember this
password = 'password123'
key = hashlib.pbkdf2_hmac(
    'sha256', # The hash digest algorithm for HMAC
    password.encode('utf-8'), # Convert the password to bytes
    salt, # Provide the salt
    100000 # It is recommended to use at least 100,000 iterations of SHA-256
)

password_to_check = 'password123' # The password provided by the user to check

# Use the exact same setup you used to generate the key, but this time put in the password to check
new_key = hashlib.pbkdf2_hmac(
    'sha256',
    password_to_check.encode('utf-8'), # Convert the password to bytes
    salt,
    100000
)

if new_key == key:
    print('Password is correct')
else:
    print('Password is incorrect')

# def PasswordMake(password):

def ConnectionString(USERNAME, PASS, HOST):
    DBstr = "mysql+pymysql://" \
            + USERNAME + \
            ":" \
            + PASS + \
            "@" \
            + HOST
    return DBstr

# Execute to DB
def ExecuteDB(cmd):
    C = DB.begin()
    C.execute(cmd)

#
# # Update dataframe. Used in like every function.
# def dfUpdate(Table):
# 	if REMOTEDB:
# 		return pd.read_sql_table(Table, con=DB, schema=SCHEMA)
# 	else:
# 		return pd.read_sql_query("SELECT * FROM " + Table, DB)

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def Login():
    if request.method == "POST":
        # getting input with name = fname in HTML form
        first_name = request.form.get("fname")
        # getting input with name = lname in HTML form
        last_name = request.form.get("lname")
        print(first_name)
        return redirect(url_for("Home"))
    return render_template("login.html")
    # return render_template("test.html", name={escape(name)})

@app.route("/home")
def Home():
    return "home"

@app.route("/<a>")
def printer(a):
    return a

print("bruh")
DB = create_engine(ConnectionString("jlt", "1234", "localhost"))  # pip install mysqlclient
a = pd.read_sql_table("user", con=DB, schema="ticketsystem")
print(a)

if __name__ == '__main__':
    app.run(debug=True)

