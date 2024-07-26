"""
creates a page in the dashboard that allows users to subscribe to an alert system
that notifies users if an operator they are interested in is suffering from an incident.
"""
import re
import logging
from os import environ

from boto3 import client
from dotenv import load_dotenv
import streamlit as st
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor


ARN_PREFIX = "arn:aws:sns:eu-west-2:129033205317:c11-trainwreck"


def get_db_connection() -> connection | None:
    """return a database connection"""
    try:
        return connect(
            host=environ['DB_IP'],
            dbname=environ['DB_NAME'],
            user=environ['DB_USERNAME'],
            password=environ['DB_PASSWORD'],
            port=environ['DB_PORT']
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error(e)
        return None


def get_db_cursor(conn: connection) -> cursor | None:
    """return a cursor object based on a given connection"""
    try:
        return conn.cursor(cursor_factory=RealDictCursor)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error(e)
        return None


def get_sns_client():
    """return an AWS SNS client using access credentials, which are environment variables."""
    try:
        return client(
            'sns',
            aws_access_key_id=environ['AWS_ACCESS_KEY'],
            aws_secret_access_key=environ['AWS_SECRET_KEY'],
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error(e)
        return None


def does_topic_arn_exist(sns_client, topic_arn: str) -> bool:
    """bool test to determine whether a topic_arn exists in the SNS client"""
    try:
        response = sns_client.get_topic_attributes(
            TopicArn=topic_arn
        )
        return response is not None
    except Exception:  # pylint: disable=broad-exception-caught
        return False


def create_topic(sns_client, operator_code: str) -> None:
    """create a topic based on the operator code a user wishes to subscribe to
    this is done if the topic does not exist in the client already"""
    sns_client.create_topic(
        Name=f"c11-trainwreck-{operator_code}"
    )


def subscribe_to_topic(sns_client, topic_arn: str, protocol: str, endpoint: str) -> None:
    """subscribe to a topic using an SNS client, given a protocol and appropriate endpoint"""
    try:
        return sns_client.subscribe(TopicArn=topic_arn, Protocol=protocol, Endpoint=endpoint)
    except Exception:  # pylint: disable=broad-exception-caught
        logging.error("Failed to subscribe user to a train alert")
        return None


def get_list_of_operators() -> list[str]:
    """return a list of all operators available to subscribe to"""
    conn = get_db_connection()

    with get_db_cursor(conn) as curs:
        curs.execute(
            """SELECT operator_code, operator_name FROM operator ORDER BY operator_name""")
        res = curs.fetchall()

    return [f"{row["operator_code"]} - {row["operator_name"]}" for row in res]


def is_email_valid(email: str) -> bool:
    """bool test to determine if this is a valid email"""
    if not email:
        return True
    email_pattern = re.compile(r"[\w\-\.]+@([\w\-]+\.)+[\w\-]{2,4}")
    return re.fullmatch(pattern=email_pattern, string=email) is not None


def is_phone_no_valid(phone_no: str) -> bool:
    """bool test to determine if a phone number is valid"""
    if not phone_no:
        return True
    number_pattern = re.compile(r"\+44 [0-9]{4} [0-9]{3} [0-9]{3}")
    return phone_no and re.fullmatch(pattern=number_pattern, string=phone_no) is not None


def get_user_contacts_from_form() -> dict | None:
    """create a subscription form for users to submit their contact information"""
    with st.form("alert_subscription", clear_on_submit=False, border=True):
        operator = st.selectbox("Select an Operator", get_list_of_operators())
        email = st.text_input("Enter your email")
        phone_no = st.text_input(
            "Enter your phone number (use the following format: +44 XXXX XXX XXX)")

        submit = st.form_submit_button()

        if operator and submit and (email or phone_no):
            valid_email = is_email_valid(email)
            valid_phone = is_phone_no_valid(phone_no)
            if valid_email and valid_phone:
                st.success(
                    f"Form submitted! you are now able to receive alerts for {operator}")
                operator = operator.split(" ")[0]
                return {"email": email, "phone": phone_no, "operator": operator}
            if not valid_email:
                st.error("Invalid email")
            if not valid_phone:
                st.error("Invalid phone number")

        return None


def deploy_alerts_page():
    """This serves as the main code for the alerts page"""
    st.title("Train Alerts")
    st.write("""Subscribe to an Operator Alert using your phone number,
             and you will receive a notification when this operator
             is affected by an incident.""")

    subscriber_inputs = get_user_contacts_from_form()

    if subscriber_inputs is not None:
        email, phone_no, operator_code = subscriber_inputs.values()
        sns_client = get_sns_client()
        subscriber_arn = f"{ARN_PREFIX}-{operator_code}"
        if not does_topic_arn_exist(sns_client, subscriber_arn):
            create_topic(sns_client, operator_code)
        if email:
            subscribe_to_topic(
                sns_client=sns_client, topic_arn=subscriber_arn, protocol="email", endpoint=email)
        if phone_no:
            subscribe_to_topic(
                sns_client=sns_client, topic_arn=subscriber_arn, protocol="sms", endpoint=phone_no)


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    deploy_alerts_page()
