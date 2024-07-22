""" Module for running the pipeline for extracting incident data from the NationalRail API."""
import logging

import extract_national
import transform_national
import load_national

FILENAME = "data.xml"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    extract_national.get_national_rail_data(FILENAME)

    incidents_data = transform_national.transform_national_rail_data(FILENAME)

    load_national.load_incidents(incidents_data)
