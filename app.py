from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

# MySQL
import pymysql
from sqlalchemy import create_engine
import cryptography

# Passwords
import hashlib
import os


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

def AccountMake(username, password):
    salt = os.urandom(32)  # Remember this
    hashed = hashlib.pbkdf2_hmac(
        'sha256',  # The hash digest algorithm for HMAC
        password.encode('utf-8'),  # Convert the password to bytes
        salt,  # Provide the salt
        100000  # It is recommended to use at least 100,000 iterations of SHA-256
    )

    ExecuteDB("INSERT INTO `ticketsystem`.`user` (`username`, `email`, `password`, `salt`) VALUES ('{username}', NULL, '{hashed}', '{salt}');", conn)

def ConnectionString(USERNAME, PASS, HOST):
    DBstr = "mysql+pymysql://" \
            + USERNAME + \
            ":" \
            + PASS + \
            "@" \
            + HOST
    return DBstr

# Execute to DB
def ExecuteDB(cmd, conn):
    with conn.connect() as C: C.execute(cmd)

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def Login():
    print(request.method)
    if request.method == "POST":
        if request.form.get('login'):
            # getting input with name = fname in HTML form
            first_name = request.form.get("fname")
            # getting input with name = lname in HTML form
            last_name = request.form.get("lname")
            print(first_name)
            return redirect(url_for("Home"))
        elif request.form.get('signup'): return redirect(url_for("Signup"))

    return render_template("login.html")


@app.route("/home")
def Home():
    return "home"

@app.route("/signup", methods=["GET", "POST"])
def Signup():
    print("bruh")
    if request.method == "POST":
        # for i in
        for i in ["password", "confirmpassword", "username", "email":]
            request.form.get(i)

    return render_template("signup.html")

print("bruh")
print(ConnectionString("jlt", "1234", "localhost"))
conn = create_engine(ConnectionString("jlt", "1234", "localhost"))  # pip install mysqlclient

# a = pd.read_sql_table("user", con=DB, schema="ticketsystem")

if __name__ == '__main__':
    app.run(debug=True)

