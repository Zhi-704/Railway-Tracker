'''Imports cleaned and loaded data from RealTime Trains API to a database'''

from os import environ as ENV
import logging

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


def get_id_if_exists(cur: DBCursor, table_name: str, conditions: dict) -> bool:
    '''Checks if a certain data value already exists inside a table'''
    query = f'''SELECT {table_name}_id FROM {table_name} WHERE {
        ' AND '.join([f'{key} = %s' for key in conditions.keys()])}'''
    cur.execute(query, tuple(conditions.values()))
    id = cur.fetchone()
    return id[0] if id is not None else None


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
            station_id = cur.fetchone()
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

    cur.close()
    conn.close()

    return


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    load_dotenv()
    data = [get_realtime_trains_data("LDS"), get_realtime_trains_data("LST")]
    modified_data = process_all_stations(data)
    import_to_database(modified_data)

    # location_dict = {
    #     "name": "The Dreaded Station of the Pizza Man",
    #     "crs": "PIZ"
    # }
    # conn = get_connection()
    # cur = get_cursor(conn)

    # print(insert_or_get_station(location_dict, conn, cur))

    # cur.close()
    # conn.close()
