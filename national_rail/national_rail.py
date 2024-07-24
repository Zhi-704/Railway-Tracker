""" Module for running the pipeline for extracting incident data from the NationalRail API."""
import logging
from dotenv import load_dotenv

from extract_national import get_national_rail_data
from transform_national import transform_national_rail_data
from load_national import load_incidents
from sns_reporting import send_message

FILENAME = "/tmp/data.xml"


def main(_event, _context):
    """
    Main function to execute the ETL (Extract, Transform, Load) pipeline.

    - Configures logging with a warning level and a specific format.
    - Loads environment variables from a .env file using dotenv.
    - Fetches national data using get_national_rail_data().
    - Transforms the fetched data using transform_national_rail_data().
    - Loads the transformed data into a database using load_incidents().
    - Alert any subscribers of any recent incidents.
    """

    logging.getLogger().setLevel(logging.INFO)
    load_dotenv()
    try:
        logging.info("Pipeline has started.")
        get_national_rail_data(FILENAME)
        logging.info("Extract has finished.")

        incidents_data = transform_national_rail_data(FILENAME)
        logging.info("Transformation has finished.")
        if not incidents_data:
            logging.info("No incidents found.")
        else:
            load_incidents(incidents_data)
            logging.info("Load has finished.")
            send_message(incidents_data)
            logging.info("Messaging has finished.")

    except Exception as e:
        logging.error("An error occurred during ETL pipeline execution: %s", e)

    logging.info("Pipeline has ended.")
