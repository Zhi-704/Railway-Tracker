"""
creates a page in the dashboard that allows users to subscribe to a summary report that
is emailed to them every day. These reports are also stored in an S3 bucket
"""
import re
from boto3 import client
from dotenv import load_dotenv
import streamlit as st
from os import environ
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor


def get_s3_client() -> client:
    """return an S3 client"""
    try:
        s3_client = client('s3',
                           aws_access_key_id=environ['AWS_ACCESS_KEY'],
                           aws_secret_access_key=environ['AWS_SECRET_KEY'])
        return s3_client
    except Exception as e:
        print(e)
        return None


def get_ses_client() -> client:
    """return an SES client"""
    try:
        s3_client = client('ses',
                           aws_access_key_id=environ['AWS_ACCESS_KEY'],
                           aws_secret_access_key=environ['AWS_SECRET_KEY'])
        return s3_client
    except Exception as e:
        print(e)
        return None


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
    except Exception as e:
        print(e)
        return None


def get_db_cursor(conn: connection) -> cursor:
    """return a cursor object based on a given connection"""
    try:
        return conn.cursor(cursor_factory=RealDictCursor)
    except Exception as e:
        print(e)
        return None


def is_email_already_subscribed(email: str, conn: connection) -> bool:
    """check if the email given has already subscribed to the database"""
    with get_db_cursor(conn) as curs:
        curs.execute(f"""SELECT COUNT(*) FROM users WHERE email='{email}'""")
        res = curs.fetchone()

    return res == 1


def is_email_valid(email: str) -> bool:
    """return a bool based on whether this is a valid email"""
    emaiL_regex = re.compile(r"^[\w\-\.]+@([\w\-]+\.)+[\w\-]{2,4}$")
    return re.match(pattern=emaiL_regex, string=email) is not None


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
            st.success(f"Email entered: {email}")
            return {'email': email}

    return {}


def deploy_page():
    """"""
    st.title("Summary Report")
    st.subheader(
        "If you wish to subscribe to a daily report on our tracking results, submit your email below.")
    input = get_from_subscription_form()
    ses = get_ses_client()
    conn = get_db_connection()

    if input.get("email", None) and is_email_already_subscribed(input["email"], conn):
        st.error("This email is already subscribed to the summary report.")


if __name__ == "__main__":
    load_dotenv()
    deploy_page()
