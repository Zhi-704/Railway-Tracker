""" Module for running the pipeline for extracting incident data from the NationalRail API."""
import logging

from extract_national import get_national_rail_data
from transform_national import transform_national_rail_data
from load_national import load_incidents

FILENAME = "data.xml"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    get_national_rail_data(FILENAME)

    incidents_data = transform_national_rail_data(FILENAME)

    if not incidents_data:
        logging.info("No incidents found.")
    else:
        load_incidents(incidents_data)
