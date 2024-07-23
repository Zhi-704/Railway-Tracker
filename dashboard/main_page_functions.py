"""
"""

import datetime as dt
from os import environ

from boto3 import client
from dotenv import load_dotenv
import streamlit as st
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor

load_dotenv()

def get_db_connection() -> connection | None:
    """return a database connection"""
    try:
        return connect(
            host=environ['DB_HOST'],
            dbname=environ['DB_NAME'],
            user=environ['DB_USERNAME'],
            password=environ['DB_PASSWORD'],
            port=environ['DB_PORT']
        )
    except Exception as e: # pylint: disable=broad-exception-caught
        st.write(e)
        return None


def get_db_cursor(conn: connection) -> cursor | None:
    """return a cursor object based on a given connection"""
    try:
        return conn.cursor(cursor_factory=RealDictCursor)
    except Exception as e: # pylint: disable=broad-exception-caught
        st.write(e)
        return None

def convert_datetime_to_string(input_date: dt.datetime) -> str:
    """"""
    try:
        return dt.datetime.strftime(input_date, "%d-%m-%Y")
    except ValueError:
        return ""

def get_closest_scheduled_incident() -> str:
    """return the information on the closest incident scheduled
    after the current time."""
    conn = get_db_connection()
    with get_db_cursor(conn) as curs:
        curs.execute("""SELECT incident_summary, incident_start FROM incident WHERE incident_start >= CURRENT_DATE ORDER BY incident_start""")
        res = curs.fetchone()
    conn.close()
    return f"{convert_datetime_to_string(res["incident_start"])}: {res["incident_summary"]}"