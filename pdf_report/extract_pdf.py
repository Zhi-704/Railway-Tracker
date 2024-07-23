"""Gather the details on train from the RDS database"""

from os import environ
import logging

from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor


def get_connection() -> connection:
    """Retrieves connection and returns it."""
    load_dotenv()
    logging.info("Retrieving database connection")
    return connect(
        user=environ['DB_USERNAME'],
        password=environ['DB_PASSWORD'],
        host=environ['DB_IP'],
        port=environ['DB_PORT'],
        dbname=environ['DB_NAME']
    )


def get_cursor(conn: connection) -> cursor:
    """Retrieves cursor and returns it."""
    logging.info("Retrieving database cursor")
    return conn.cursor(cursor_factory=RealDictCursor)


def extract_pdf() -> list[tuple]:
    """Extracts data from the RDS database."""
    conn = get_connection()
    with get_cursor(conn) as cur:
        cur.execute("""SELECT * FROM waypoint
                    JOIN station USING (station_id)""")
        data = cur.fetchall()

    logging.info("Extract: successful")
    return data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    extract_pdf()
