"""
creates a page in the dashboard that allows users to subscribe to an alert system
that notifies users if an operator they are interested in is suffering from an incident.
"""
import re
from os import environ

import streamlit as st
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor

def get_db_connection() -> connection:
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
        print(e)
        return None


def get_db_cursor(conn: connection) -> cursor:
    """return a cursor object based on a given connection"""
    try:
        return conn.cursor(cursor_factory=RealDictCursor)
    except Exception as e: # pylint: disable=broad-exception-caught
        st.write(e)
        return None
    

def deploy_alerts_page():
    """This serves as the main code for the alerts page"""
    st.title("Train Alerts")
    st.write("""Subscribe to an Operator Alert using your phone number, 
             and you will receive a notification when this operator
             is affected by an incident.""")
    


if __name__ == "__main__":
    deploy_alerts_page()