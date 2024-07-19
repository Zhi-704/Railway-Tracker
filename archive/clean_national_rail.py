""" This module works with old NationalRail incident data from the RDS and 
    deletes incident data that is no longer needed."""

import logging

from db_connection import get_connection, execute_without_result


def clean_national_rail_incidents() -> None:
    """ Cleans NationalRail Incidents from RDS -  deletes incidents with end dates that have passed.
        This also deletes affected operators (ON DELETE CASCADE)."""

    with get_connection() as conn:
        query = """
        DELETE FROM incident
        WHERE incident_end < TIMEZONE('Europe/London', CURRENT_TIMESTAMP);
        """

        execute_without_result(conn, query, ())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    clean_national_rail_incidents()
