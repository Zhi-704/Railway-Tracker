'''Imports cleaned and loaded data from RealTime Trains API to a database'''

from os import environ as ENV
import logging
from datetime import datetime, timedelta

from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extras import DictCursor
from psycopg2.extensions import connection as DBConnection, cursor as DBCursor

from extract_real import get_api_data_of_all_stations
from transform_real import process_all_stations

CANCELLATION_FIELDS = ["cancelReasonCode",
                       "cancelReasonLongText"]


def get_connection() -> DBConnection:
    """Creates a database session and returns a connection object."""
    return connect(
        host=ENV["DB_IP"],
        port=ENV["DB_PORT"],
        user=ENV["DB_USERNAME"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"],
    )


def get_cursor(conn: DBConnection) -> DBCursor:
    """Creates and returns a cursor to execute RDS commands (PostgreSQL)."""
    return conn.cursor(cursor_factory=DictCursor)


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


def insert_or_get_waypoint(station_id: int,
                           service_id: int,
                           service_dict: dict,
                           conn: DBConnection,
                           cur: DBCursor):
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
            return existing_id

        query = '''
        INSERT INTO waypoint (
            run_date, booked_arrival, actual_arrival, booked_departure, actual_departure, service_id, station_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING waypoint_id
        '''

        cur.execute(query, (
            run_date,
            booked_arrival,
            actual_arrival,
            booked_departure,
            actual_departure,
            service_id,
            station_id
        ))
        waypoint_id = cur.fetchone()[0]
        conn.commit()
        return waypoint_id

    except Exception as e:  # pylint: disable=broad-exception-caught
        conn.rollback()
        logging.error(
            "Load: Error occurred inserting Waypoint: %s", e)
        return None


def insert_or_get_cancellation(cancel_code_id: int,
                               waypoint_id: int,
                               conn: DBConnection,
                               cur: DBCursor):
    '''Inserts a cancelled journey into the database'''
    cancellations_conditions = {
        'cancel_code_id': cancel_code_id,
        'waypoint_id': waypoint_id
    }

    return insert_or_get_entry('cancellation',
                               cancellations_conditions,
                               cancellations_conditions,
                               "number",
                               conn,
                               cur)


def insert_or_get_cancel_code(cancelled_service_loc: dict, conn: DBConnection, cur: DBCursor):
    '''Inserts a cancel code into the database'''
    cancel_code_conditions = {
        'cancel_code': cancelled_service_loc["cancelReasonCode"]
    }

    insert_values = {
        'cancel_code': cancelled_service_loc["cancelReasonCode"],
        'cause':  cancelled_service_loc["cancelReasonLongText"]
    }

    return insert_or_get_entry('cancel_code',
                               insert_values,
                               cancel_code_conditions,
                               cancelled_service_loc["cancelReasonCode"],
                               conn,
                               cur)


def insert_or_get_service(service_dict: dict,
                          operator_id: int,
                          conn: DBConnection,
                          cur: DBCursor) -> int:
    '''Insert or get operator id from the database'''
    service_conditions = {
        'service_uid': service_dict["serviceUid"]
    }

    insert_values = {
        'operator_id': operator_id,
        'service_uid': service_dict["serviceUid"]
    }

    return insert_or_get_entry('service',
                               insert_values,
                               service_conditions,
                               service_dict["serviceUid"],
                               conn,
                               cur)


def insert_or_get_operator(service_dict: dict, conn: DBConnection, cur: DBCursor) -> int:
    '''Insert or get operator id from the database'''
    operator_conditions = {
        'operator_code': service_dict["atocCode"]
    }

    insert_values = {
        'operator_code': service_dict["atocCode"],
        'operator_name': service_dict["atocName"]
    }

    return insert_or_get_entry('operator',
                               insert_values,
                               operator_conditions,
                               service_dict["atocCode"],
                               conn,
                               cur)


def insert_or_get_station(location_dict: dict, conn: DBConnection, cur: DBCursor) -> int:
    '''Insert or get station id from the database'''
    station_conditions = {
        'station_crs': location_dict["crs"]
    }

    insert_values = {
        'station_crs': location_dict["crs"],
        'station_name': location_dict["name"]
    }

    return insert_or_get_entry('station',
                               insert_values,
                               station_conditions,
                               location_dict["crs"],
                               conn,
                               cur)


def insert_or_get_entry(table_name: str,
                        insert_values: dict,
                        unique_data_conditions: dict,
                        entry_name: str,
                        conn: DBConnection,
                        cur: DBCursor) -> int:
    '''Insert or get an entry's id from the database'''

    table_id = get_id_if_exists(cur, table_name, unique_data_conditions)
    columns = ', '.join(insert_values.keys())

    if table_id is None:
        columns = ', '.join(insert_values.keys())
        num_of_values = ', '.join(['%s'] * len(insert_values))
        query = f'''
        INSERT INTO {table_name} ({columns})
        VALUES
        ({num_of_values})
        RETURNING {table_name}_id
        '''

        try:
            cur.execute(query, tuple(insert_values.values()))
            table_id = cur.fetchone()[0]
            conn.commit()
        except Exception as e:  # pylint: disable=broad-exception-caught
            conn.rollback()
            logging.error("Load: Error occurred inserting %s %s: %s",
                          table_name.capitalize(), entry_name, e)
            table_id = None

    return table_id


def import_to_database(stations: list[dict]) -> None:
    '''Import data retrieved to the database'''
    conn = get_connection()
    cur = get_cursor(conn)

    for station in stations:
        logging.info("Processing station %s...", station["location"]["crs"])
        station_id = insert_or_get_station(station["location"], conn, cur)
        for service in station["services"]:
            operator_id = insert_or_get_operator(service, conn, cur)
            service_id = insert_or_get_service(service, operator_id, conn, cur)
            waypoint_id = insert_or_get_waypoint(
                station_id, service_id, service, conn, cur)

            for key in service["locationDetail"]:
                if key in CANCELLATION_FIELDS:
                    cancel_code_id = insert_or_get_cancel_code(
                        service["locationDetail"], conn, cur)
                    insert_or_get_cancellation(
                        cancel_code_id, waypoint_id, conn, cur)
                    break
        logging.info("Station %s processed with %s waypoints.",
                     station["location"]["crs"], len(station["services"]))

    cur.close()
    conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    load_dotenv()
    data = get_api_data_of_all_stations()
    modified_data = process_all_stations(data)
    print("\n-------------------------")
    import_to_database(modified_data)
