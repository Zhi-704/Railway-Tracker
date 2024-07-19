"""Gets the information from the RealTime Trains API"""

import json
from os import environ as ENV
from datetime import datetime, timedelta
import logging

from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
from requests import get

import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection as DBConnection, cursor as DBCursor


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


def get_api_url(station_code: str, date: str) -> str:
    """Constructs the API URL for the given station code and date."""
    base_url = "https://api.rtt.io/api/v1/json/search"
    return f"{base_url}/{station_code}/{date}"


def get_data_from_api(url: str, username: str, password: str) -> dict | None:
    """Retrieves data from the realtime trains API and returns the response as a dictionary."""
    try:
        response = get(url, auth=HTTPBasicAuth(username, password), timeout=10)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logging.error(
            "Extract: Error occurred while fetching data from API: %s", e)
        logging.error(
            "Extract: Error occurred for url: %s", url)
        return None


def save_data_to_file(json_data: list[dict], filename: str) -> None:
    """Saves the provided data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(json_data, file, indent=4)


def get_yesterday_data_of_station(station_code: str) -> dict | None:
    """Retrieves data from realtime trains API for the given station code and saves it to a file"""

    username = ENV.get("REALTIME_USERNAME")
    password = ENV.get("REALTIME_PASSWORD")

    if not username or not password:
        logging.error(
            "Extract: Username and password are required environment variables.")
        return None

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y/%m/%d")
    logging.info("Retrieving data...")
    api_url = get_api_url(station_code, yesterday)

    station_data = get_data_from_api(api_url, username, password)
    if station_data:
        logging.info(
            "Data successfully retrieved for station %s.", station_code)
        return station_data
    logging.error(
        "Extract: Failed to retrieve station %s from the API.", station_code)
    return None


def get_all_stations_crs() -> list[str]:
    '''Grabs all stations crs from the database'''

    conn = get_connection()
    cur = get_cursor(conn)

    query = '''
SELECT station_crs
FROM station
'''

    cur.execute(query)
    crs_data = cur.fetchall()
    return [crs[0] for crs in crs_data]


def get_api_data_of_all_stations() -> list[dict] | None:
    '''Gets all station data from the API'''

    list_of_crs = get_all_stations_crs()
    list_of_stations = []

    for crs in list_of_crs:
        station_data = get_yesterday_data_of_station(crs)
        if station_data:
            list_of_stations.append(station_data)

    logging.info(
        "Data successfully retrieved for all stations.")
    return list_of_stations


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    load_dotenv()
    data = get_api_data_of_all_stations()
    save_data_to_file(data, "data3.json")
