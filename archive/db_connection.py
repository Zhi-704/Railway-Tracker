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


def execute(conn: connection, query: str, data: tuple) -> dict | None:
    """ Executes SQL queries on AWS RDS, and returns result.
        Uses fetchall(). """

    try:
        cur = get_cursor(conn)

        cur.execute(query, (data))

        conn.commit()
        result = cur.fetchall()
        cur.close()

        logging.info("Clean: successful for: %s", (data))

    except Exception as e:
        conn.rollback()
        logging.error(
            "Clean: Error occurred when executing cleaning for: %s", (e))

    return result


def execute_without_result(conn: connection, query: str, data: tuple) -> None:
    """ Executes SQL queries on AWS RDS. """

    try:
        cur = get_cursor(conn)

        cur.execute(query, (data))

        conn.commit()
        cur.close()
        logging.info("Clean: successful: %s", data)

    except Exception as e:
        conn.rollback()
        logging.error("Clean: Error occurred when executing cleaning - %s", e)
