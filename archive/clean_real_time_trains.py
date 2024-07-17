""" This module works with old RealTimeTrains waypoint data from the RDS and 
    archives train data that is no longer needed. The archive contains the 
    performance metrics of the train data."""

from os import environ
import logging

from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extensions import connection

import connect


def get_month_old_waypoints(conn: connection):
    """ Retrieves all waypoints that have a run_date of a month ago or more. """

    query = """
        SELECT *
        FROM waypoint
        WHERE run_date <= CURRENT_DATE - INTERVAL '1 month';
    """

    try:
        cur = connect.get_cursor(conn)
        cur.execute(query)

        conn.commit()
        waypoints = cur.fetchall()
        cur.close()
        logging.info("Clean: Deleted old incidents. ")

    except Exception as e:
        conn.rollback()
        logging.error("Clean: Error occurred when cleaning incidents %s", e)

    return waypoints


def clean_real_time_trains_data():
    """ Cleans RealTimeTrains waypoints data from RDS based on how long ago the train journey
        occurred. Computed Performance statistics for the archiving process."""

    conn = connect.get_connection()

    # 1) get based on run date ->
    old_waypoints = get_month_old_waypoints(conn)
    print(old_waypoints)

    # 2) compute performance metrics
    # deal with cancellations and services that they are connected to - delete from DB
    # add to archive db

    conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    clean_real_time_trains_data()
