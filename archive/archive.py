""" This module works with old data from the RDS and archives it for
    long term storage, otherwise deletes data that is no longer needed."""

import logging

from clean_national_rail import clean_national_rail_incidents
from clean_real_time_trains import clean_real_time_trains_data


def clean_rail_tracker():
    """ Cleans rail Tracker of any out dated data, archives necessary 
        information."""

    logging.info("Clean: Began cleaning process.")

    clean_national_rail_incidents()
    clean_real_time_trains_data()

    logging.info("Clean: Completed cleaning process.")


def handler(_event, _context):
    """ Main lambda function to execute cleaning the Railway tracker:
        1. cleans national rail incident data 
        2. cleans and archives the real time train data """

    logging.getLogger().setLevel(logging.INFO)
    clean_rail_tracker()


if __name__ == "__main__":
    handler(None, None)
