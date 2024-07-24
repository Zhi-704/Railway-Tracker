"""
creates a page in the dashboard that allows users to subscribe to a summary report that
is emailed to them every day. These reports are also stored in an S3 bucket
"""
import re
from os import environ
from dotenv import load_dotenv
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
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(e)
        return None


def get_db_cursor(conn: connection) -> cursor:
    """return a cursor object based on a given connection"""
    try:
        return conn.cursor(cursor_factory=RealDictCursor)
    except Exception as e:  # pylint: disable=broad-exception-caught
        st.write(e)
        return None


def is_email_already_subscribed(email: str, conn: connection) -> bool:
    """check if the email given has already subscribed to the database"""
    with get_db_cursor(conn) as curs:
        curs.execute(
            "SELECT COUNT(*) FROM subscriber WHERE email=%s", (email, ))
        res = curs.fetchone()
    return res["count"] == 1


def is_email_valid(email: str) -> bool:
    """return a bool based on whether this is a valid email"""
    email_pattern = re.compile(r"^[\w\-\.]+@([\w\-]+\.)+[\w\-]{2,4}$")
    return re.match(pattern=email_pattern, string=email) is not None


def get_from_subscription_form() -> dict:
    """create a subscription form to the summary report"""
    email = ""
    with st.form("summary_subscription", clear_on_submit=True, border=True):
        email = st.text_input("Email:")
        submit = st.form_submit_button()

    if email != "" and submit:
        if not is_email_valid(email):
            st.error("This is not a valid email.")
        else:
            return {'email': email}
    return {}


def upload_new_subscriber(conn: connection, email: str):
    """Take the email given and attempt to upload it to the database. """
    try:
        with get_db_cursor(conn) as curs:
            curs.execute(
                "INSERT INTO subscriber (email) VALUES (%s)", (email, ))
            conn.commit()
        return 1
    except Exception as e:  # pylint: disable=broad-exception-caught
        st.write(e)
        return None


def deploy_subscription_page():
    """This contains the main code for the subscription page."""
    st.title("Summary Report")
    st.subheader(
        "Subscribe to a daily report on our tracking results by adding your email below.")
    subscriber_input = get_from_subscription_form()
    conn = get_db_connection()
    email = subscriber_input.get("email", None)
    if email and is_email_already_subscribed(email, conn):
        st.error("This email is already subscribed to the summary report.")
    elif email:
        if upload_new_subscriber(conn, email) is not None:
            st.success(f"{email} is now subscribed to the summary report.")
        else:
            st.error(f"An error ocurred when trying to add {
                     email} to the database.")


if __name__ == "__main__":
    load_dotenv()
    deploy_subscription_page()
