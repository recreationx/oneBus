from flask import Flask, render_template, request, redirect
from datastore import Datastore

data_creation = Datastore("busdata.db")
data_creation.init_all()

app = Flask(__name__)


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/nearestbusstop", methods=["GET", "POST"])
def nearestbusstop():
    return render_template("nearestbusstop.html")


# reminder to set debug to false for production
app.run("127.0.0.1", debug=True)
