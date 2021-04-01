import re
import csv
import json
import sqlite3

tables_dict = {
    "bus_stops_init": """
        CREATE TABLE IF NOT EXISTS busstops (
            BusStopCode INTEGER,
            RoadName TEXT,
            Description TEXT,
            Latitude REAL,
            Longitude REAL,
            PRIMARY KEY (BusStopCode)
        );
    """,
    "bus_services_init": """
        CREATE TABLE IF NOT EXISTS busservices (
            ServiceNo TEXT,
            Operator TEXT,
            Category TEXT,
            Direction INTEGER,
            PRIMARY KEY (ServiceNo)
        );
    """,
    "bus_service_info_init": """
        CREATE TABLE IF NOT EXISTS servicesinfo (
            ServiceNo TEXT,
            Direction INTEGER,
            OriginCode INTEGER,
            DestinationCode INTEGER,
            AMPeakFreq TEXT,
            AMOffpeakFreq TEXT,
            PMPeakFreq TEXT,
            PMOffpeakFreq TEXT,
            LoopDesc TEXT,
            PRIMARY KEY (ServiceNo, Direction),
            FOREIGN KEY (ServiceNo) REFERENCES busservices(ServiceNo)
        );
    """,
    "bus_route_info_init": """
        CREATE TABLE IF NOT EXISTS routeinfo (
            ServiceNo TEXT,
            Direction INTEGER,
            StopSequence INTEGER,
            BusStopCode INTEGER,
            Distance INTEGER,
            WDFirstBus INTEGER,
            WDLastBus INTEGER,
            SatFirstBus INTEGER,
            SatLastBus INTEGER,
            SunFirstBus INTEGER,
            SunLastBus INTEGER,
            PRIMARY KEY (ServiceNo, Direction, StopSequence),
            FOREIGN KEY (ServiceNo) REFERENCES busservices(ServiceNo)
        );
    """,
    "bus_fare_express_init": """
        CREATE TABLE IF NOT EXISTS expressfare (
            MinDistance REAL,
            MaxDistance REAL,
            CashFare INTEGER,
            AdultCardFare INTEGER,
            SeniorCardFare INTEGER,
            StudentCardFare INTEGER,
            WorkfareCardFare INTEGER,
            DisabilitesFare INTEGER,
            PRIMARY KEY (MinDistance, MaxDistance)
        );
    """,
    "bus_fare_feeder_init": """
        CREATE TABLE IF NOT EXISTS feederfare (
            AdultCardFare INTEGER,
            AdultCashFare INTEGER,
            SeniorCardFare INTEGER,
            SeniorCashFare INTEGER,
            StudentCardFare INTEGER,
            StudentCashFare INTEGER,
            WorkfareCardFare INTEGER,
            WorkfareCashFare INTEGER,
            DisabilitesCardFare INTEGER,
            DisabilitesCashFare INTEGER
        );
    """,
    "bus_fare_trunk_init": """
        CREATE TABLE IF NOT EXISTS trunkfare (
            MinDistance REAL,
            MaxDistance REAL,
            AdultCardFare INTEGER,
            AdultCashFare INTEGER,
            SeniorCardFare INTEGER,
            SeniorCashFare INTEGER,
            StudentCardFare INTEGER,
            StudentCashFare INTEGER,
            WorkfareCardFare INTEGER,
            WorkfareCashFare INTEGER,
            DisabilitesCardFare INTEGER,
            DisabilitesCashFare INTEGER,
            PRIMARY KEY (MinDistance, MaxDistance)
        );
    """,
}

data_insert = {
    "insert_express_fare": """
    INSERT OR IGNORE INTO expressfare VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """,
    "insert_feeder_fare": """
    INSERT OR IGNORE INTO feederfare VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """,
    "insert_trunk_fare": """
    INSERT OR IGNORE INTO trunkfare VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """,
    "insert_bus_stops": """
    INSERT OR IGNORE INTO busstops VALUES (:BusStopCode, :RoadName, :Description, :Latitude, :Longitude);
    """,
    "insert_bus_services": """
    INSERT OR IGNORE INTO busservices VALUES (?, ?, ?, ?);
    """,
    "insert_services_info": """
    INSERT OR IGNORE INTO servicesinfo VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """,
    "insert_route_info": """
    INSERT OR IGNORE INTO routeinfo VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
}

query_table = {
    "get_coord": """
    SELECT * FROM busstops;
    """,
}


class Datastore:
    def __init__(self, uri):
        """Initialize a database with given URI

        Args:
            uri (string): URI for database
        """
        self.uri = uri

    def get_conn(self):
        """Retrieves a connection with the database

        Returns:
            conn: A sqlite3 Connection object connected to stored URI
        """
        conn = sqlite3.connect(self.uri)
        conn.row_factory = sqlite3.Row
        return conn

    def get_records(self, command, param=None):
        """Retrieve records using key from query_table

        Args:
            command (str): A key in query_table
            param (tup/list, optional): parameters to pass in.
            Defaults to None.

        Returns:
            arr: Array of rows
        """
        conn = self.get_conn()
        cur = conn.cursor()
        if param is None:
            cur.execute(query_table[command])
        else:
            cur.execute(query_table[command], param)
        return cur.fetchall()

    def distance_parser(self, raw_distance):
        """[HELPER METHOD]
        Converts a raw distance string to a storable
        format for the database.

        Args:
            raw_distance (string): Raw distance string
            from fare data

        Returns:
            distance (array): A tuple/list of parsed distance
        """
        if "Up to" in raw_distance:
            distance = re.findall(r"\d+\.\d+", raw_distance)
            distance = (0, distance[0])  # Start at 0
        elif "Over" in raw_distance:
            distance = re.findall(r"\d+\.\d+", raw_distance)
            distance = (
                distance[0],
                9e99,
            )  # End with 9e99 - infinitely large number
        else:
            distance = re.findall(r"\d+\.\d+", raw_distance)
        return distance

    def tables_init(self):
        """Initializes required tables for the database"""
        conn = self.get_conn()
        cursor = conn.cursor()
        for table_commands in tables_dict.keys():
            cursor.execute(tables_dict[table_commands])

        conn.commit()
        conn.close()

    def fare_init(self):
        """Load fare data into respective tables"""
        conn = self.get_conn()
        cursor = conn.cursor()

        # Fare init
        with open(
            "raw_data/fare_data/fares-for-express-bus-services-effective-from-28-december-2019.csv",
            "r+",
        ) as f:
            express_fare_data = csv.DictReader(f)
            for fares_entry in express_fare_data:
                distance = self.distance_parser(fares_entry["distance"])
                cursor.execute(
                    data_insert["insert_express_fare"],
                    (
                        distance[0],
                        distance[1],
                        fares_entry["cash_fare_per_ride"],
                        fares_entry["adult_card_fare_per_ride"],
                        fares_entry["senior_citizen_card_fare_per_ride"],
                        fares_entry["student_card_fare_per_ride"],
                        fares_entry["workfare_transport_concession_card_fare_per_ride"],
                        fares_entry["persons_with_disabilities_card_fare_per_ride"],
                    ),
                )

        with open(
            "raw_data/fare_data/fares-for-trunk-bus-services-effective-from-28-december-2019.csv",
            "r+",
        ) as f:
            trunk_fare_data = csv.DictReader(f)
            for fares_entry in trunk_fare_data:
                distance = self.distance_parser(fares_entry["distance"])
                cursor.execute(
                    data_insert["insert_trunk_fare"],
                    (
                        distance[0],
                        distance[1],
                        fares_entry["adult_card_fare_per_ride"],
                        fares_entry["adult_cash_fare_per_ride"],
                        fares_entry["senior_citizen_card_fare_per_ride"],
                        fares_entry["senior_citizen_cash_fare_per_ride"],
                        fares_entry["student_card_fare_per_ride"],
                        fares_entry["student_cash_fare_per_ride"],
                        fares_entry["workfare_transport_concession_card_fare_per_ride"],
                        fares_entry["workfare_transport_concession_cash_fare_per_ride"],
                        fares_entry["persons_with_disabilities_card_fare_per_ride"],
                        fares_entry["persons_with_disabilities_cash_fare_per_ride"],
                    ),
                )

        with open(
            "raw_data/fare_data/fares-for-feeder-bus-services-effective-from-28-december-2019.csv",
            "r+",
        ) as f:
            feeder_fare_data = csv.DictReader(f)
            for fares_entry in feeder_fare_data:
                cursor.execute(
                    data_insert["insert_feeder_fare"],
                    (
                        fares_entry["adult_card_fare_per_ride"],
                        fares_entry["adult_cash_fare_per_ride"],
                        fares_entry["senior_citizen_card_fare_per_ride"],
                        fares_entry["senior_citizen_cash_fare_per_ride"],
                        fares_entry["student_card_fare_per_ride"],
                        fares_entry["student_cash_fare_per_ride"],
                        fares_entry["workfare_transport_concession_card_fare_per_ride"],
                        fares_entry["workfare_transport_concession_cash_fare_per_ride"],
                        fares_entry["persons_with_disabilities_card_fare_per_ride"],
                        fares_entry["persons_with_disabilities_cash_fare_per_ride"],
                    ),
                )

        conn.commit()
        conn.close()

    def bus_init(self):
        """Load bus related data into respective tables"""
        conn = self.get_conn()
        cursor = conn.cursor()
        with open("raw_data/bus_data/BusStops.json", "r+") as f:
            data = json.load(f)
            cursor.executemany(data_insert["insert_bus_stops"], data)
        with open("raw_data/bus_data/BusServices.json", "r+") as f:
            data = json.load(f)
            for entry in data:
                cursor.execute(
                    data_insert["insert_bus_services"],
                    (
                        entry["ServiceNo"],
                        entry["Operator"],
                        entry["Category"],
                        entry["Direction"],
                    ),
                )
                cursor.execute(
                    data_insert["insert_services_info"],
                    (
                        entry["ServiceNo"],
                        entry["Direction"],
                        entry["OriginCode"],
                        entry["DestinationCode"],
                        entry["AM_Peak_Freq"],
                        entry["AM_Offpeak_Freq"],
                        entry["PM_Peak_Freq"],
                        entry["PM_Offpeak_Freq"],
                        entry["LoopDesc"],
                    ),
                )
        with open("raw_data/bus_data/BusRoutes.json", "r+") as f:
            data = json.load(f)
            for entry in data:
                cursor.execute(
                    data_insert["insert_route_info"],
                    (
                        entry["ServiceNo"],
                        entry["Direction"],
                        entry["StopSequence"],
                        entry["BusStopCode"],
                        entry["Distance"],
                        entry["WD_FirstBus"],
                        entry["WD_LastBus"],
                        entry["SAT_FirstBus"],
                        entry["SAT_LastBus"],
                        entry["SUN_FirstBus"],
                        entry["SUN_LastBus"],
                    ),
                )

        conn.commit()
        conn.close()

    def init_all(self):
        """Initialize all related data at one go"""
        self.tables_init()
        self.fare_init()
        self.bus_init()
        print("DATASTORE: ALL OK")
