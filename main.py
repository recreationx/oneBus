from flask import Flask, render_template, request, jsonify
from datastore import Datastore
from algorithms import haversine, findDistance
from checks import isFloat

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

    TODO: implement AJAX for static loading DONE
    """
    if (
        request.method == "POST"
        and request.form["latitudetext"]
        and request.form["longitudetext"]
        and request.form["recordmax"]
    ):
        latitude = request.form["latitudetext"]
        longitude = request.form["longitudetext"]
        recordmax = request.form["recordmax"]
        if isFloat(latitude) and isFloat(longitude) and isFloat(recordmax):
            recordmax = int(
                round(float(recordmax))
            )  # error handling jic that recordmax is a float
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
            return jsonify(
                {"data": render_template("temp.html", results=distances[:recordmax])}
            )

    return render_template("nearestbusstop.html")


@app.route("/farecalculator", methods=["GET", "POST"])
def farecalc():
    if request.method == "GET":
        busservices = datastore.get_records("get_busservices")
        return render_template("farecalculator.html", busservices=busservices)

    if request.method == "POST":
        if request.form["type"] == "getDirections":
            serviceno = request.form["value"]
            directions = datastore.get_records("get_busserviceinfo", (serviceno,))
            directions_list = []
            for direction in directions:
                originstop = datastore.get_records(
                    "get_desc_from_code", (direction["OriginCode"],)
                )[0]["Description"]
                deststop = datastore.get_records(
                    "get_desc_from_code", (direction["DestinationCode"],)
                )[0]["Description"]
                if direction["Direction"] == "1":
                    text = "".join(["FROM ", originstop, " TO ", deststop])
                else:
                    text = "".join(["FROM ", deststop, " TO ", originstop])

                directions_list.append(
                    {
                        "value": (
                            direction["OriginCode"],
                            direction["DestinationCode"],
                        ),
                        "text": text,
                    }
                )

            return jsonify(data=directions_list)


@app.route("/help", methods=["GET", "POST"])
def help():
    return render_template("help.html")


@app.errorhandler(404)
def page_not_found(e):
    return "The resource could not be found."


# reminder to set debug to false for production
if __name__ == "__main__":
    app.run(debug=True)
