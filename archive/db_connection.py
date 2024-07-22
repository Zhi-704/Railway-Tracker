""" Module for connecting to the database and executing queries on the database. """

from os import environ
import logging

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


def execute(conn: connection, query: str, data: tuple) -> list[dict] | None:
    """ Executes SQL queries on AWS RDS, and returns result.
        Uses fetchall(). """

    query_command = query.strip().split(" ")[0]

    with get_cursor(conn) as cur:
        try:
            cur = get_cursor(conn)
            cur.execute(query, (data))
            conn.commit()

            logging.info("Clean: successful for %s, for %s.",
                         query_command, data)

        except Exception as e:
            conn.rollback()
            logging.error("Clean: Error occurred for %s -  %s.",
                          query_command, e)

        try:
            result = cur.fetchall()

        except Exception as e:
            result = None

    return result
