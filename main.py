from flask import Flask, render_template, request, jsonify
from datastore import Datastore
from validation import Validator
from features import FareCalculator, NearestBus

# Initialize datastore
datastore = Datastore("busdata.db")
datastore.init_all()

# Initialize app features
nearestbus = NearestBus(datastore)
farecalculator = FareCalculator(datastore)

# Initialize validation
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

    NOTE: Rendering a external HTML file is a workaround
    to prevent the error from Google Map API where it could
    not find the element to load into upon DOM load completion
    (aka bus stop search not carried out thus no map can exist)
    """

    if request.method == "GET":
        return render_template("nearestbusstop.html")

    if request.method == "POST":
        if validator.inputCheck(request.form):
            latitude = request.form["latitudetext"]
            longitude = request.form["longitudetext"]
            recordmax = request.form["recordmax"]
            return jsonify(
                {
                    "data": render_template(
                        "bustable.html",
                        results=nearestbus.getBusStops(latitude, longitude, recordmax),
                    )
                }
            )
        else:
            return jsonify(
                {
                    "data": render_template(
                        "bustable.html",
                        error="Please input all fields and ensure that they are valid numbers.",
                    )
                }
            )


@app.route("/farecalculator", methods=["GET", "POST"])
def farecalculate():
    """Calculate fare given fare type, direction, boarding stop,
    alighting stop and service number

    NOTE:
    1. No need for data validation because no manual input
    is needed
    2. Due to insufficient data for some fare types (SBST, CITY LINK),
    the search will sometimes not work and database search will
    return None. In this case, please search another service.
    Currently unknown fare types defaults to EXPRESS fare.
    3. Did not directly pass variables into functions for more readability

    """
    if request.method == "GET":
        busservices = datastore.get_records("get_busservices")
        return render_template("farecalculator.html", busservices=busservices)

    if request.method == "POST":
        if request.form["type"] == "getDirections":
            serviceno = request.form["serviceno"]

            return jsonify(data=farecalculator.getDirections(serviceno))

        if request.form["type"] == "getBoardingAt":
            direction = request.form["direction"]
            serviceno = request.form["serviceno"]

            return jsonify(data=farecalculator.getBoardingAt(direction, serviceno))

        if request.form["type"] == "getAlightingAt":
            direction = request.form["direction"]
            serviceno = request.form["serviceno"]
            boardingno = request.form["boardingat"]

            return jsonify(
                data=farecalculator.getAlightingAt(direction, serviceno, boardingno)
            )

        if request.form["type"] == "addJourney":
            faretype = request.form["faretype"]
            serviceno = request.form["busserviceno"]
            direction = request.form["direction"]
            boardingno = request.form["boardingat"]
            alightingno = request.form["alightingat"]

            if validator.selectCheck(
                faretype, serviceno, direction, boardingno, alightingno
            ):
                return jsonify(
                    {
                        "data": render_template(
                            "faretable.html",
                            results=farecalculator.calculateFare(
                                faretype, direction, serviceno, boardingno, alightingno
                            ),
                        )
                    }
                )
            else:
                return jsonify(
                    {
                        "data": render_template(
                            "faretable.html",
                            error="Please select a valid option for all fields.",
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
