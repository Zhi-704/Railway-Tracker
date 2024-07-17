""" Loads incident data into the RDS database. """
from os import environ
from dotenv import load_dotenv

from psycopg2 import connect
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor, execute_values

import transform  # just for development


def get_connection() -> connection:
    """ Retrieves connection and returns it. """
    load_dotenv()
    return connect(
        user=environ['DB_USERNAME'],
        password=environ['DB_PASSWORD'],
        host=environ['DB_IP'],
        port=environ['DB_PORT'],
        dbname=environ['DB_NAME']
    )


def get_cursor(conn: connection) -> cursor:
    """ Retrieves cursor and returns it. """
    return conn.cursor(cursor_factory=RealDictCursor)


def upload_affected_operator_assignment(conn: connection, incident_id: int, operator_code: str) -> None:

    query = """
        INSERT INTO affected_operator (incident_number, operator_code)
        VALUES (%s, %s)
    """

    cur = get_cursor(conn)
    cur.execute(query, (incident_id, operator_code))

    conn.commit()
    cur.close()


def upload_incident(incident: dict) -> int:
    """ Takes an incident and uploads to the database, returning the incident id. """
    # or do execute many with all incidents.

    # then iterate through each incident and upload operators to operator assignment table.
    # if operator doesn't exist; add it.


def load_incidents(incidents_data: list[dict]) -> None:
    """ Loads all incidents created within the last 5 minutes to the RDS. """
    conn = get_connection()

    for incident in incidents_data:
        print(incident['incident_number'])

    conn.close()


if __name__ == "__main__":
    load_incidents(transform.transform_national_rail_data("testing.xml"))
    # just for development
