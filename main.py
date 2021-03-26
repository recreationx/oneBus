from flask import Flask, render_template, request, redirect
from datastore import Datastore

data = Datastore("busdata.db")
data.init_all()

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def main():
    return render_template("index.html")


@app.route("/nearestbusstop", methods=["GET", "POST"])
def nearestbusstop():
    """Find the nearest bus stop from a given coordinate
    Coordinate can be retrieved automatically or
    manually entered

    1. Take in given coordinate

    TODO: implement AJAX for static loading
    """
    conn = data.get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM busstops
        """
    )
    a = cur.fetchall()
    print(a)

    return render_template("nearestbusstop.html")


# reminder to set debug to false for production
if __name__ == "__main__":
    app.run(debug=True)
