'''Imports cleaned and loaded data from RealTime Trains API to a database'''

from os import environ as ENV
import logging

from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection as DBConnection, cursor as DBCursor


def get_connection() -> DBConnection:
    """Creates a database session and returns a connection object."""
    return psycopg2.connect(
        host=ENV["DB_IP"],
        port=ENV["DB_PORT"],
        user=ENV["DB_USERNAME"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"],
    )


def get_cursor(connection: DBConnection) -> DBCursor:
    """Creates and returns a cursor to execute RDS commands (PostgreSQL)."""
    return connection.cursor(cursor_factory=psycopg2.extras.DictCursor)


if __name__ == "__main__":
    load_dotenv()
