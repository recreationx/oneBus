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
            direction_val = 0
            directions_list = []
            for direction in directions:
                originstop = datastore.get_records(
                    "get_desc_from_code", (direction["OriginCode"],)
                )[0]["Description"]
                deststop = datastore.get_records(
                    "get_desc_from_code", (direction["DestinationCode"],)
                )[0]["Description"]
                text = "".join(["FROM ", originstop, " TO ", deststop])
                if direction["Direction"] == 1:
                    direction_val = 1
                elif direction["Direction"] == 2:
                    direction_val = 2

                directions_list.append(
                    {
                        "value": (direction_val,),
                        "text": text,
                    }
                )

            print(directions_list)

            return jsonify(data=directions_list)

        if request.form["type"] == "getBoardingAt":
            boardingdir = request.form["direction"]
            bsNo = request.form["bsNo"]
            results = datastore.get_records(
                "get_busroutes",
                (
                    bsNo,
                    boardingdir,
                ),
            )
            print(results)
            boardingAtList = []
            for i in results:
                boardingAtList.append(
                    {
                        "value": (i["StopSequence"],),
                        "text": datastore.get_records(
                            "get_desc_from_code", (i["BusStopCode"],)
                        )[0]["Description"],
                    }
                )

            return jsonify(data=boardingAtList)

        if request.form["type"] == "getAlightingAt":
            boardingdir = request.form["direction"]
            bsNo = request.form["bsNo"]
            boardingno = request.form["boardingNo"]
            results = datastore.get_records(
                "get_busroutes",
                (
                    bsNo,
                    boardingdir,
                ),
            )
            print(results)
            boardingAtList = []
            for i in results:
                boardingAtList.append(
                    {
                        "value": (i["StopSequence"],),
                        "text": datastore.get_records(
                            "get_desc_from_code", (i["BusStopCode"],)
                        )[0]["Description"],
                    }
                )

            return jsonify(data=boardingAtList[int(boardingno) :])

        if request.form["type"] == "addJourney":
            faretype = request.form["faretype"]
            busserviceno = request.form["busserviceno"]
            direction = request.form["direction"]
            boardingat = request.form["boardingat"]
            alightingat = request.form["alightingat"]
            categorymapping = {
                "SBST": "get_expressfare",
                "INDUSTRIAL": "get_expressfare",
                "CITY_LINK": "get_expressfare",
                "TRUNK": "get_trunkfare",
                "EXPRESS": "get_expressfare",
                "FEEDER": "feederfare",
            }
            faremapping = {
                "0": "AdultCardFare",
                "1": "SeniorCardFare",
                "2": "StudentCardFare",
                "3": "WorkfareCardFare",
                "4": "DisabilitesCardFare",
            }
            print(faretype, busserviceno, direction, boardingat, alightingat)
            category = categorymapping[
                datastore.get_records("get_category", (busserviceno,))[0]["Category"]
            ]
            boardingdist = datastore.get_records(
                "get_distance", (busserviceno, direction, boardingat)
            )[0]["Distance"]
            alightingdist = datastore.get_records(
                "get_distance", (busserviceno, direction, alightingat)
            )[0]["Distance"]
            dist = float(alightingdist) - float(boardingdist)
            fare = datastore.get_records(category, (dist,))[0][faremapping[faretype]]

            results = [
                {
                    "Service": busserviceno,
                    "Distance": dist,
                    "Board": boardingat,
                    "Alight": alightingat,
                    "Fare": fare,
                }
            ]

            return jsonify(
                {"data": render_template("journeyrender.html", results=results)}
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
