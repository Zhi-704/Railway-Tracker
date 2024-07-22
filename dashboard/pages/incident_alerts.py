"""
creates a page in the dashboard that allows users to subscribe to an alert system
that notifies users if an operator they are interested in is suffering from an incident.
"""
import re
from os import environ

from boto3 import client
from dotenv import load_dotenv
import streamlit as st
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor

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
        print(e)
        return None


def get_db_cursor(conn: connection) -> cursor | None:
    """return a cursor object based on a given connection"""
    try:
        return conn.cursor(cursor_factory=RealDictCursor)
    except Exception as e: # pylint: disable=broad-exception-caught
        st.write(e)
        return None
    
def get_sns_client():
    """return an AWS SNS client using access credentials, which are environment variables."""
    try:
        return client(
            'sns',
            aws_access_key_id=environ['AWS_ACCESS_KEY'],
            aws_secret_access_key=environ['AWS_SECRET_KEY'],
            )
    except Exception as e: # pylint: disable=broad-exception-caught
        st.write(e)
        return None
    
def get_list_of_operators() -> list[str]:
    """"""
    conn = get_db_connection()

    with get_db_cursor(conn) as curs:
        curs.execute("""SELECT operator_code, operator_name FROM operator ORDER BY operator_name""")
        res = curs.fetchall()
    
    return [f"{row["operator_code"]} - {row["operator_name"]}" for row in res]
    


def get_user_contacts_from_form() -> dict | None:
    """create a subscription form for users to submit their contact information."""
    with st.form("alert_subscription", clear_on_submit=True, border=True):


        operator = st.selectbox("Select an Operator", get_list_of_operators())

        email = st.text_input("Enter your email")
        phone_no = st.text_input("Enter your phone number")

        submit = st.form_submit_button()

        if operator and submit and (email or phone_no):
            pass

def deploy_alerts_page():
    """This serves as the main code for the alerts page"""
    st.title("Train Alerts")
    st.write("""Subscribe to an Operator Alert using your phone number, 
             and you will receive a notification when this operator
             is affected by an incident.""")
    
    subscriber_inputs = get_user_contacts_from_form()
    


if __name__ == "__main__":
    load_dotenv()
    deploy_alerts_page()