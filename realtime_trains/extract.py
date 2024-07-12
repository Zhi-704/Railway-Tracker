"""Gets the information from the realtime trains api"""

import json
from os import path, environ as ENV
from datetime import datetime

from requests.auth import HTTPBasicAuth
from requests import get
from dotenv import load_dotenv

CRS = "LST"


def get_data_from_api() -> None:
    """Gets the data from the realtime trains api and saves it to a file"""
    load_dotenv()

    base_url = "https://api.rtt.io/api/v1/json/search"
    yesterday = datetime.now().strftime("%Y/%m/%d")

    url = path.join(base_url, CRS, yesterday)

    username = ENV["USERNAME"]
    password = ENV["PASSWORD"]

    response = get(url, auth=HTTPBasicAuth(username, password), timeout=10)

    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(response.json(), file, indent=4)


if __name__ == "__main__":
    get_data_from_api()
