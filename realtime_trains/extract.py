"""Gets the information from the realtime trains API"""

import json
from os import environ as ENV
from datetime import datetime, timedelta
import logging

from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
from requests import get
from dotenv import load_dotenv


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
        logging.error("Error occurred while fetching data from API: %s", e)
        return None


def save_data_to_file(data: dict, filename: str) -> None:
    """Saves the provided data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def get_realtime_trains_data(station_code: str, output_file: str) -> None:
    """Retrieves data from the realtime trains API for the given station code and saves it to a file."""
    load_dotenv()

    username = ENV.get("USERNAME")
    password = ENV.get("PASSWORD")

    if not username or not password:
        logging.error(
            "Username and password are required environment variables.")
        return

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y/%m/%d")
    api_url = get_api_url(station_code, yesterday)

    data = get_data_from_api(api_url, username, password)
    if data:
        save_data_to_file(data, output_file)
    else:
        logging.error("Failed to retrieve data from the API.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    get_realtime_trains_data("LDS", "data.json")
