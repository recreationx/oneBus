from flask import Flask, render_template, request, jsonify
from datastore import Datastore
from checks import Validator
from features import FareCalculator, NearestBus

datastore = Datastore("busdata.db")
datastore.init_all()
nearestbus = NearestBus(datastore)
farecalculator = FareCalculator(datastore)
validator = Validator()

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
    
    if request.method == "GET":
        return render_template("nearestbusstop.html")
        
    if (
        request.method == "POST"
        and validator.paramCheckExist(['latitudetext', 'longitudetext', 'recordmax'], request.form.keys())
    ):
        latitude = request.form["latitudetext"]
        longitude = request.form["longitudetext"]
        recordmax = request.form["recordmax"]
        if validator.isFloat(latitude) and validator.isFloat(longitude) and validator.isFloat(recordmax):
            return jsonify(
                {"data": render_template("temp.html", results=nearestbus.getBusStops(latitude, longitude, recordmax))}
            )


@app.route("/farecalculator", methods=["GET", "POST"])
def farecalc():
    if request.method == "GET":
        busservices = datastore.get_records("get_busservices")
        return render_template("farecalculator.html", busservices=busservices)

    if request.method == "POST":
        if request.form["type"] == "getDirections":
            serviceno = request.form["value"]

            return jsonify(data=farecalculator.getDirections(serviceno))

        if request.form["type"] == "getBoardingAt":
            direction = request.form["direction"]
            serviceno = request.form["bsNo"]

            return jsonify(data=farecalculator.getBoardingAt(direction, serviceno))

        if request.form["type"] == "getAlightingAt":
            direction = request.form["direction"]
            serviceno = request.form["bsNo"]
            boardingno = request.form["boardingNo"]

            return jsonify(
                data=farecalculator.getAlightingAt(direction, serviceno, boardingno)
            )

        if request.form["type"] == "addJourney":
            faretype = request.form["faretype"]
            serviceno = request.form["busserviceno"]
            direction = request.form["direction"]
            boardingno = request.form["boardingat"]
            alightingno = request.form["alightingat"]

            return jsonify(
                {
                    "data": render_template(
                        "journeyrender.html",
                        results=farecalculator.calculateFare(
                            faretype, direction, serviceno, boardingno, alightingno
                        ),
                    )
                }
            )


@app.route("/help", methods=["GET", "POST"])
def help():
    return render_template("help.html")


@app.errorhandler(404)
def page_not_found(e):
    return "The resource could not be found."


# reminder to set debug to false for production
if __name__ == "__main__":
    app.run(debug=True)
