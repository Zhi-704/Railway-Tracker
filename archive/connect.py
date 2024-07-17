from os import environ

from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor


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
