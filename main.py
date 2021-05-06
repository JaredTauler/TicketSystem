import flask
from flask import Flask, render_template, request, escape
from sqlalchemy import create_engine
import pandas as pd

# DB = create_engine("sqlite:///1.db")
# a = pd.read_sql_table("item", con=DB)

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def Login():
    if request.method == "POST":
        # getting input with name = fname in HTML form
        first_name = request.form.get("fname")
        # getting input with name = lname in HTML form
        last_name = request.form.get("lname")
        print(first_name)
        return "Your name is " + first_name + last_name
    return render_template("test.html")
    # return render_template("test.html", name={escape(name)})

@app.route("/<a>")
def printer(a):
    return a

if __name__ == '__main__':
    app.run(debug=True)

