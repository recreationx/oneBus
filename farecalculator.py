class FareCalculator:
    def __init__(self, database):
        """Initialize FareCalculator with a given Datastore

        Args:
            database (instance): An instance of Datastore
        """
        self.db = database

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
        return self.getBoardingAt(direction, serviceno)[int(boardingno) :]

    def calculateFare(self, faretype, direction, serviceno, boardingno, alightingno):
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