from flask import Flask, render_template, request, redirect, jsonify
from datastore import Datastore
from algorithms import haversine, findDistance

datastore = Datastore("busdata.db")
datastore.init_all()

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
    if (
        request.method == "POST"
        and request.form["latitudetext"]
        and request.form["longitudetext"]
    ):
        latitude = request.form["latitudetext"]
        longitude = request.form["longitudetext"]
        stops_coord = datastore.get_records("get_coord")
        distances = []
        for coords in stops_coord:
            stop_dict = dict(coords)
            stop_dict["Distance"] = haversine(
                float(longitude),
                float(latitude),
                coords["Longitude"],
                coords["Latitude"],
            )
            distances.append(stop_dict)
        distances = findDistance(distances)
        return jsonify({"data": render_template("temp.html", results=distances[:10])})

    return render_template("nearestbusstop.html")


# reminder to set debug to false for production
if __name__ == "__main__":
    app.run(debug=True)
