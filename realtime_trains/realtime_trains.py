'''ETL pipeline for extracting, cleaning, and loading data from RealTime Trains API to a database'''


import logging
from dotenv import load_dotenv

from extract_real import get_api_data_of_all_stations
from transform_real import process_all_stations
from load_real import import_to_database


def main(event, context):  # pylint: disable=unused-argument
    """
    Main function to execute the ETL (Extract, Transform, Load) pipeline.

    - Configures logging with a warning level and a specific format.
    - Loads environment variables from a .env file using dotenv.
    - Fetches trains data using get_api_data_of_all_stations().
    - Transforms the fetched data using process_all_stations().
    - Loads the transformed data into a database using import_to_database().
    """

    logging.getLogger().setLevel(logging.INFO)

    try:
        load_dotenv()
        print("Pipeline has started.")
        data = get_api_data_of_all_stations()
        print("Extract finished.")
        modified_data = process_all_stations(data)
        print("Transformation finished.")
        import_to_database(modified_data)
        print("Load finished.")
        print("Pipeline has finished.")

    except Exception as e:
        logging.error("An error occurred during ETL pipeline execution: %s", e)
