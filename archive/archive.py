""" This module works with old data from the RDS and archives it for
    long term storage, otherwise deletes data that is no longer needed."""

import logging

import clean_national_rail as nr_cleaner
import clean_real_time_trains as rtt_cleaner


def clean_rail_tracker():
    """ Cleans rail Tracker of any out dated data, archives necessary 
        information."""

    logging.info("Clean: Began cleaning process.")

    nr_cleaner.clean_national_rail_incidents()

    rtt_cleaner.clean_real_time_trains_data()

    logging.info("Clean: Completed cleaning process.")


def handler(event, context):
    # pylint: disable=unused-argument
    """ Main lambda function to execute cleaning the Railway tracker:
        1. cleans national rail incident data 
        2. cleans and archives the real time train data """

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    clean_rail_tracker()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    clean_rail_tracker()
