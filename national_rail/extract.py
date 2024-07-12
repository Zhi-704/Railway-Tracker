"""Gets the information from the national rail api"""

from os import environ as ENV

from requests import get
from dotenv import load_dotenv


def get_data_from_api() -> None:
    """Gets the data from the national rail api and saves it to a file"""
    load_dotenv()

    url = "https://api1.raildata.org.uk/1010-knowlegebase-incidents-xml-feed1_0/incidents.xml"

    headersDict = {
        "x-apikey": ENV["APIKEY"],
        "User-Agent": ""
    }

    response = get(url, headers=headersDict, timeout=10)

    with open("data.xml", "w", encoding="utf-8") as file:
        file.write(response.text)


if __name__ == "__main__":
    get_data_from_api()
