""" Module for running the pipeline for extracting incident data from the NationalRail API."""
import logging

import extract
import transform
import load

FILENAME = "data.xml"     # 'test_data.xml'

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    extract.get_national_rail_data(FILENAME)

    incidents_data = transform.transform_national_rail_data(FILENAME)

    load.load_incidents(incidents_data)
