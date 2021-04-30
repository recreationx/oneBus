from algorithms import haversine, findDistance


class Feature:
    """
    Parent class for any new feature
    """

    def __init__(self, database):
        """Initialize a feature requiring db access with a given
        Datastore object

        Args:
            database (instance): An instance of Datastore
        """
        self.db = database

    def get_record(self, command, param=None):
        """Further abstraction on top of existing Datastore
        get_record method to reduce redundant code

        Retrieve a single record using key from query_table

        Args:
            command (str): A key in query_table
            param (tup/list, optional): parameters to pass in.
            Defaults to None.

        Returns:
            arr: Array of rows
        """
        return self.db.get_record(command, param)

    def get_records(self, command, param=None):
        """Further abstraction on top of existing Datastore
        get_records method to reduce redundant code

        Retrieve records using key from query_table


        Args:
            command (str): A key in query_table
            param (tup/list, optional): parameters to pass in.
            Defaults to None.

        Returns:
            arr: Array of rows
        """
        return self.db.get_records(command, param)


class NearestBus(Feature):
    """Nearest Bus Stop Finder Feature

    Args:
        Feature (class): Parent class
    """

    def getBusStops(self, latitude, longitude, recordmax):
        """Retrieve a sorted list of bus stops from a given latitude
        and longitude, truncated to a specified recordmax length

        Args:
            latitude (str/int): Latitude value
            longitude (str/int): Longitude value
            recordmax (str/int): Maximum number of records to display

        Returns:
            list: List of bus stops truncated to recordmax length
            for display on front-end
        """
        recordmax = int(
            round(float(recordmax))
        )  # error handling jic that recordmax is a float
        stops_coord = self.get_records("get_coord")
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
    """Fare Calculator Feature

    Args:
        Feature (class): Parent class
    """

    def getDirections(self, serviceno):
        """Generates a list of directions for a given bus service no
        with its origin and ending bus stop names
        Args:
            serviceno (str): Bus Service No

        Returns:
            directions_list (list): Populated directions list for display on frontend
        """
        directions_list = []
        directions = self.get_records("get_busserviceinfo", (serviceno,))
        for direction in directions:
            originstop = self.get_records(
                "get_desc_from_code", (direction["OriginCode"],)
            )[0]["Description"]
            endstop = self.get_records(
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
            direction (str): direction value either 1 or 2
            serviceno (str): Bus Service No

        Returns:
            displayBoarding (list): Populated bus stop list for display on frontend
        """
        busroute = self.get_records(
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
                    "text": self.get_records(
                        "get_desc_from_code", (stop["BusStopCode"],)
                    )[0]["Description"],
                }
            )

        return displayBoarding

    def getAlightingAt(self, direction, serviceno, boardingno):
        """Generates a list of bus stop names for a given bus service
        and direction truncated to a given boarding stop

        Args:
            direction (str): direction value either 1 or 2
            serviceno (str): Bus Service No
            boardingno (str): Boarding stop number on the route

        Returns:
            list: Populated list of able-to-alight stations after boarding station
        """
        return self.getBoardingAt(direction, serviceno)[int(boardingno) :]

    def calculateFare(self, faretype, direction, serviceno, boardingno, alightingno):
        """Generate a list of a single dictionary containing fare information
        to feed to front end

        Args:
            faretype (str)): Fare type
            direction (str): direction value either 1 or 2
            serviceno (str): Bus Service No
            boardingno (str): Boarding stop number on the route
            alightingno (str): Alighting stop number on the route

        Returns:
            displayFare (list): Calculated results to feed to frontend
        """

        categorymapping = {
            "SBST": "get_expressfare",
            "INDUSTRIAL": "get_expressfare",
            "CITY_LINK": "get_expressfare",
            "TRUNK": "get_trunkfare",
            "EXPRESS": "get_expressfare",
            "FEEDER": "get_feederfare",
        }
        faremapping = {
            "0": "AdultCardFare",
            "1": "SeniorCardFare",
            "2": "StudentCardFare",
            "3": "WorkfareCardFare",
            "4": "DisabilitesCardFare",
        }
        category = categorymapping[
            self.get_record("get_category", (serviceno,))["Category"]
        ]
        boardingdist = self.get_record(
            "get_distance", (serviceno, direction, boardingno)
        )["Distance"]
        alightingdist = self.get_record(
            "get_distance", (serviceno, direction, alightingno)
        )["Distance"]
        dist = float(alightingdist) - float(boardingdist)
        if category == "get_feederfare":
            fare = self.get_record(category)[faremapping[faretype]]
        else:
            fare = self.get_record(category, (dist,))[faremapping[faretype]]
        alightingname = self.getBoardingAt(direction, serviceno)[int(alightingno) - 1][
            "text"
        ]
        boardingname = self.getBoardingAt(direction, serviceno)[int(boardingno) - 1][
            "text"
        ]

        displayFare = [
            {
                "Service": serviceno,
                "Distance": dist,
                "Board": boardingname,
                "Alight": alightingname,
                "Fare": fare,
            }
        ]

        return displayFare
