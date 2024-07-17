""" This module works with old NationalRail incident data from the RDS and 
    deletes incident data that is no longer needed."""

import logging

from psycopg2.extensions import connection
import db_connection


def delete_old_incidents(conn: connection) -> None:
    """ Deletes incidents with end dates that have passed and are no longer required 
        for storage."""

    query = """
        DELETE FROM incident
        WHERE incident_end < TIMEZONE('Europe/London', CURRENT_TIMESTAMP);
    """

    try:
        cur = db_connection.get_cursor(conn)
        cur.execute(query)

        conn.commit()
        cur.close()
        logging.info("Clean: Deleted old incidents. ")

    except Exception as e:
        conn.rollback()
        logging.error("Clean: Error occurred when cleaning incidents %s", e)


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
