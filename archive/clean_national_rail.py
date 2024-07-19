""" This module works with old NationalRail incident data from the RDS and 
    deletes incident data that is no longer needed."""

import logging

from psycopg2.extensions import connection
import db_connection


def delete_old_incidents(conn: connection) -> None:
    """ Deletes incidents with end dates that have passed and are no longer required 
        for storage. This also deletes affected operators (ON DELETE CASCADE)"""

    query = """
        DELETE FROM incident
        WHERE incident_end < TIMEZONE('Europe/London', CURRENT_TIMESTAMP);
    """

    db_connection.execute_without_result(conn, query, ())


def clean_national_rail_incidents() -> None:
    """ Cleans NationalRail Incidents from the RDS based on whether the incident has ended 
        or not."""

    conn = db_connection.get_connection()
    delete_old_incidents(conn)
    conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    clean_national_rail_incidents()
