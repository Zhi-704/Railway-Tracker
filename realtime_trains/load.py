'''Imports cleaned and loaded data from RealTime Trains API to a database'''

from os import environ as ENV
import logging
from datetime import datetime, timedelta

from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection as DBConnection, cursor as DBCursor

from extract import get_realtime_trains_data
from transform import process_all_stations

REQUIRED_FIELDS_SERVICE_LOCATION_DETAILS = ["displayAs", "tiploc", "crs"]
REQUIRED_FIELDS_SERVICE = ["locationDetail",
                           "serviceUid", "atocCode", "atocName"]
REQUIRED_FIELDS_LOCATION = ["name", "crs"]
CANCELLATION_FIELDS = ["cancelReasonCode",
                       "cancelReasonLongText"]


def get_connection() -> DBConnection:
    """Creates a database session and returns a connection object."""
    return psycopg2.connect(
        host=ENV["DB_IP"],
        port=ENV["DB_PORT"],
        user=ENV["DB_USERNAME"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"],
    )


def get_cursor(conn: DBConnection) -> DBCursor:
    """Creates and returns a cursor to execute RDS commands (PostgreSQL)."""
    return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def get_id_if_exists(cur: DBCursor, table_name: str, conditions: dict[any]) -> int | None:
    '''Checks if a certain data value already exists inside a table and retrieves their id'''
    where_clauses = []
    values = []
    for key, value in conditions.items():
        if value is None:
            where_clauses.append(f"{key} IS NULL")
        else:
            where_clauses.append(f"{key} = %s")
            values.append(value)

    query = f'''SELECT {table_name}_id FROM {table_name}
        WHERE {' AND '.join(where_clauses)}'''
    cur.execute(query, tuple(values))
    table_id = cur.fetchone()
    return table_id[0] if table_id is not None else None


def insert_or_get_cancellation(cancel_code_id: int, waypoint_id: int, conn: DBConnection, cur: DBCursor):
    '''Inserts a cancelled journey into the database'''
    cancellations_conditions = {
        'cancel_code_id': cancel_code_id,
        'waypoint_id': waypoint_id
    }

    cancellation_id = get_id_if_exists(
        cur, "cancellation", cancellations_conditions)

    if cancellation_id is None:
        query = '''
        INSERT INTO cancellation (cancel_code_id, waypoint_id)
        VALUES
        (%s, %s)
        RETURNING cancellation_id
        '''

        try:
            cur.execute(query, (
                cancel_code_id,
                waypoint_id
            ))
            cancellation_id = cur.fetchone()[0]
            logging.info("Cancellation %s added!",
                         cancellation_id)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(
                "Load: Error occurred inserting cancellation: %s", e)
            cancellation_id = None
    else:
        logging.info("Cancellation %s retrieved!",
                     cancellation_id)

    return cancellation_id


def insert_or_get_cancel_code(cancelled_service_loc: dict, conn: DBConnection, cur: DBCursor):
    '''Inserts a cancel code into the database'''
    cancel_code_conditions = {
        'cancel_code': cancelled_service_loc["cancelReasonCode"]
    }

    cancel_code_id = get_id_if_exists(
        cur, "cancel_code", cancel_code_conditions)
    if cancel_code_id is None:
        query = '''
        INSERT INTO cancel_code (cancel_code, cause)
        VALUES
        (%s, %s)
        RETURNING cancel_code_id
        '''

        try:
            cur.execute(query, (
                cancelled_service_loc["cancelReasonCode"],
                cancelled_service_loc["cancelReasonLongText"]
            ))
            cancel_code_id = cur.fetchone()[0]
            logging.info("Cancel Code %s added!",
                         cancelled_service_loc["cancelReasonCode"])
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(
                "Load: Error occurred inserting Cancel Code: %s", e)
            cancel_code_id = None
    else:
        logging.info("Cancel Code %s retrieved!",
                     cancelled_service_loc["cancelReasonCode"])

    return cancel_code_id


def insert_or_get_waypoint(station_id: int, service_id: int, service_dict: dict, conn: DBConnection, cur: DBCursor):
    '''Inserts or gets a journey from the database'''

    location_detail = service_dict["locationDetail"]

    try:
        run_date = datetime.strptime(service_dict["runDate"], "%Y-%m-%d")

        booked_arrival_str = location_detail.get("gbttBookedArrival")
        actual_arrival_str = location_detail.get("realtimeArrival")
        booked_departure_str = location_detail.get("gbttBookedDeparture")
        actual_departure_str = location_detail.get("realtimeDeparture")

        booked_arrival = None
        actual_arrival = None
        booked_departure = None
        actual_departure = None

        if booked_arrival_str:
            booked_arrival_day = run_date + \
                timedelta(days=1) if location_detail.get(
                    "gbttBookedArrivalNextDay", False) else run_date
            booked_arrival = booked_arrival_day.replace(
                hour=int(booked_arrival_str[:2]), minute=int(booked_arrival_str[2:]))

        if actual_arrival_str:
            actual_arrival_day = run_date + \
                timedelta(days=1) if location_detail.get(
                    "realtimeArrivalNextDay", False) else run_date
            actual_arrival = actual_arrival_day.replace(
                hour=int(actual_arrival_str[:2]), minute=int(actual_arrival_str[2:]))

        if booked_departure_str:
            booked_departure_day = run_date + \
                timedelta(days=1) if location_detail.get(
                    "gbttBookedDepartureNextDay", False) else run_date
            booked_departure = booked_departure_day.replace(
                hour=int(booked_departure_str[:2]), minute=int(booked_departure_str[2:]))

        if actual_departure_str:
            actual_departure_day = run_date + \
                timedelta(days=1) if location_detail.get(
                    "realtimeDepartureNextDay", False) else run_date
            actual_departure = actual_departure_day.replace(
                hour=int(actual_departure_str[:2]), minute=int(actual_departure_str[2:]))

        conditions = {
            "run_date": run_date,
            "booked_arrival": booked_arrival,
            "actual_arrival": actual_arrival,
            "booked_departure": booked_departure,
            "actual_departure": actual_departure,
            "service_id": service_id,
            "station_id": station_id
        }
        existing_id = get_id_if_exists(cur, "waypoint", conditions)
        if existing_id:
            logging.info("Retrieved Waypoint with ID: %s", existing_id)
            return existing_id

        query = '''
        INSERT INTO waypoint (
            run_date, booked_arrival, actual_arrival, booked_departure, actual_departure, service_id, station_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING waypoint_id
        '''

        cur.execute(query, (
            run_date, booked_arrival, actual_arrival, booked_departure, actual_departure, service_id, station_id
        ))
        waypoint_id = cur.fetchone()[0]
        conn.commit()
        logging.info("Inserted Waypoint with ID: %s", waypoint_id)

    except Exception as e:
        conn.rollback()
        logging.error(
            "Load: Error occurred inserting Waypoint: %s", e)
        return None


def insert_or_get_service(service_dict: dict, operator_id: int, conn: DBConnection, cur: DBCursor) -> int:
    '''Insert or get operator id from the database'''
    service_conditions = {
        'service_uid': service_dict["serviceUid"]
    }

    service_id = get_id_if_exists(cur, "service", service_conditions)
    if service_id is None:
        query = '''
        INSERT INTO service (operator_id, service_uid)
        VALUES
        (%s, %s)
        RETURNING service_id
        '''

        try:
            cur.execute(query, (
                operator_id,
                service_dict["serviceUid"]
            ))
            service_id = cur.fetchone()[0]
            logging.info("Service %s added!", service_dict["serviceUid"])
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(
                "Load: Error occurred inserting Service: %s", e)
            service_id = None
    else:
        logging.info("Service %s retrieved!", service_dict["serviceUid"])

    return service_id


def insert_or_get_operator(service_dict: dict, conn: DBConnection, cur: DBCursor) -> int:
    '''Insert or get operator id from the database'''
    operator_conditions = {
        'operator_code': service_dict["atocCode"]
    }

    operator_id = get_id_if_exists(cur, "operator", operator_conditions)
    if operator_id is None:
        query = '''
        INSERT INTO operator (operator_code, operator_name)
        VALUES
        (%s, %s)
        RETURNING operator_id
        '''

        try:
            cur.execute(query, (
                service_dict["atocCode"],
                service_dict["atocName"]
            ))
            operator_id = cur.fetchone()[0]
            logging.info("Operator %s added!", service_dict["crs"])
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(
                "Load: Error occurred inserting Operator: %s", e)
            operator_id = None
    else:
        logging.info("Operator %s retrieved!", service_dict["atocCode"])

    return operator_id


def insert_or_get_station(location_dict: dict, conn: DBConnection, cur: DBCursor) -> int:
    '''Insert or get station id from the database'''
    station_conditions = {
        'station_crs': location_dict["crs"]
    }

    station_id = get_id_if_exists(cur, "station", station_conditions)
    if station_id is None:
        query = '''
        INSERT INTO station (station_crs, station_name)
        VALUES
        (%s, %s)
        RETURNING station_id
        '''

        try:
            cur.execute(query, (
                location_dict["crs"],
                location_dict["name"]
            ))
            station_id = cur.fetchone()[0]
            logging.info("Station %s added!", location_dict["crs"])
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(
                "Load: Error occurred inserting station: %s", e)
            station_id = None
    else:
        logging.info("Station %s retrieved!", location_dict["crs"])

    return station_id


def import_to_database(stations: list[dict]) -> None:
    '''Import data retrieved to the database'''
    conn = get_connection()
    cur = get_cursor(conn)

    for station in stations:
        station_id = insert_or_get_station(station["location"], conn, cur)
        for service in station["services"]:
            operator_id = insert_or_get_operator(service, conn, cur)
            service_id = insert_or_get_service(service, operator_id, conn, cur)
            waypoint_id = insert_or_get_waypoint(
                station_id, service_id, service, conn, cur)

            for key in service["locationDetail"]:
                if key in CANCELLATION_FIELDS:
                    print("ENTERED!!!!!!")
                    cancel_code_id = insert_or_get_cancel_code(
                        service["locationDetail"], conn, cur)
                    insert_or_get_cancellation(
                        cancel_code_id, waypoint_id, conn, cur)
                    break

            print("\n-----------------------------")

    cur.close()
    conn.close()

    return


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    load_dotenv()
    data = [get_realtime_trains_data("LDS")]
    data[0]["services"] = data[0]["services"][:200]
    modified_data = process_all_stations(data)
    import_to_database(modified_data)
