from algorithms import haversine, findDistance


class Feature:
    def __init__(self, database):
        """Initialize a feature requiring db access with a given
        Datastore URI

        Args:
            database (instance): An instance of Datastore
        """
        self.db = database


class NearestBus(Feature):
    def getBusStops(self, latitude, longitude, recordmax):
        recordmax = int(
            round(float(recordmax))
        )  # error handling jic that recordmax is a float
        stops_coord = self.db.get_records("get_coord")
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
        return distances[:recordmax]


class FareCalculator(Feature):
    def getDirections(self, serviceno):
        """Generates a list of directions for a given bus service no
        with its origin and ending bus stop names
        Args:
            serviceno (str): Bus Service No

        Returns:
            directions_list (list): Populated directions list for display on frontend
        """
        directions_list = []
        directions = self.db.get_records("get_busserviceinfo", (serviceno,))
        for direction in directions:
            originstop = self.db.get_records(
                "get_desc_from_code", (direction["OriginCode"],)
            )[0]["Description"]
            endstop = self.db.get_records(
                "get_desc_from_code", (direction["DestinationCode"],)
            )[0]["Description"]
            displaytext = "FROM " + str(originstop) + " TO " + str(endstop)
            directions_list.append(
                {
                    "value": (direction["Direction"],),
                    "text": displaytext,
                }
            )

        return directions_list

    def getBoardingAt(self, direction, serviceno):
        """Generates a list of bus stop names for a given bus service
        and direction

        Args:
            direction (int): direction value either 1 or 2
            serviceno (int): Bus Service No

        Returns:
            displayBoarding (list): Populated bus stop list for display on frontend
        """
        busroute = self.db.get_records(
            "get_busroutes",
            (
                serviceno,
                direction,
            ),
        )
        displayBoarding = []
        for stop in busroute:
            displayBoarding.append(
                {
                    "value": (stop["StopSequence"],),
                    "text": self.db.get_records(
                        "get_desc_from_code", (stop["BusStopCode"],)
                    )[0]["Description"],
                }
            )

        return displayBoarding

    def getAlightingAt(self, direction, serviceno, boardingno):
        """Generates a list of bus stop names for a given bus service
        and direction truncated to a given boarding stop

        Args:
            direction (int): direction value either 1 or 2
            serviceno (int): Bus Service No
            boardingno (int): Boarding stop number on the route

        Returns:
            list: Populated list of able-to-alight stations after boarding station
        """
        return self.getBoardingAt(direction, serviceno)[int(boardingno) :]

    def calculateFare(self, faretype, direction, serviceno, boardingno, alightingno):
        """Generate a list of a single dictionary containing fare information
        to feed to front end

        Args:
            faretype (str)): Fare type
            direction (int): direction value either 1 or 2
            serviceno (int): Bus Service No
            boardingno (int): Boarding stop number on the route
            alightingno (int): Alighting stop number on the route

        Returns:
            displayFare (list): Calculated results to feed to frontend
        """
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
        category = categorymapping[
            self.db.get_record("get_category", (serviceno,))["Category"]
        ]
        boardingdist = self.db.get_record(
            "get_distance", (serviceno, direction, boardingno)
        )["Distance"]
        alightingdist = self.db.get_record(
            "get_distance", (serviceno, direction, alightingno)
        )["Distance"]
        dist = float(alightingdist) - float(boardingdist)
        fare = self.db.get_record(category, (dist,))[faremapping[faretype]]

        displayFare = [
            {
                "Service": serviceno,
                "Distance": dist,
                "Board": boardingno,
                "Alight": alightingno,
                "Fare": fare,
            }
        ]

        return displayFare
