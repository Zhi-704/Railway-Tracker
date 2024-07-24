'''Script used for notifying all subscribed users of incidents for their operators.'''


import json
from os import environ as ENV
import logging
from datetime import datetime

from dotenv import load_dotenv
from boto3 import client
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor
from psycopg2 import connect

FILTER_TOPICS_BY = "c11-trainwreck-"


def get_connection() -> connection:
    """ Retrieves connection and returns it. """
    load_dotenv()
    return connect(
        user=ENV['DB_USERNAME'],
        password=ENV['DB_PASSWORD'],
        host=ENV['DB_IP'],
        port=ENV['DB_PORT'],
        dbname=ENV['DB_NAME']
    )


def get_cursor(conn: connection) -> cursor:
    """ Retrieves cursor and returns it. """
    return conn.cursor(cursor_factory=RealDictCursor)


def get_sns_client() -> client:
    '''Creates sns client'''
    return client('sns',
                  aws_access_key_id=ENV["ACCESS_KEY"],
                  aws_secret_access_key=ENV["SECRET_ACCESS_KEY"],
                  region_name='eu-west-2')


def get_topics_arns_from_aws(sns_client: client) -> list[dict]:
    '''Gets all available topics on AWS'''
    response = sns_client.list_topics()
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return response['Topics']
    return None


def filter_topics(filter_word: str, topic_list: list[dict]) -> list[dict]:
    '''Filters list of topics with relevant topics that have a specific word'''
    return [topic for topic in topic_list if filter_word in topic['TopicArn']]


def extract_operator_code(topic_arn: str) -> str:
    '''Extracts the operator code from the topic arn'''
    if topic_arn is None or not isinstance(topic_arn, str):
        return None
    raw_str = topic_arn.split(':')[-1]
    parts = raw_str.split('-')[2:]
    return ' '.join(parts)


def extract_operator_to_dictionary(ops_list: list[dict]) -> list[dict]:
    '''Grabs the operator from list of arns'''
    for op_arn in ops_list:
        topic_arn = op_arn['TopicArn']
        op_code = extract_operator_code(topic_arn)
        op_arn['shortcode'] = op_code
    return ops_list


def find_common_elements(list1: list, list2: list) -> list:
    """
    Finds common elements between two lists and 
    returns a list of elements that are present in both lists.
    """
    set_list2 = set(list2)
    return [element for element in list1 if element in set_list2]


def transform_datetime_string(input_string: str) -> str | None:
    """
    Transforms a datetime string from 'YYYY-MM-DDTHH:MM:SS.SSS+HH:MM' format
    to 'YYYY-MM-DD HH:MM' format.
    """
    try:
        dt = datetime.strptime(input_string, "%Y-%m-%dT%H:%M:%S.%f%z")
        output_string = dt.strftime("%Y-%m-%d %H:%M")
        return output_string
    except Exception:
        return None


def publish_multi_message(sns_client,
                          topic_arn,
                          subject: str,
                          default_message: str,
                          sms_message: str,
                          email_message: str) -> int:
    """Publishes a multi-format message to a topic."""
    try:
        message = {
            "default": default_message,
            "sms": sms_message,
            "email": email_message,
        }
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message),
            Subject=subject,
            MessageStructure="json"
        )
        message_id = response["MessageId"]
        logging.info("Published multi-format message to topic %s.", topic_arn)
    except ClientError:
        logging.exception("Couldn't publish message to topic %s.", topic_arn)
    else:
        return message_id
    return None


def publish_list_to_topic(sns_client: client,
                          topic_arn: str,
                          operator_code: str,
                          incidents_list: list[dict]) -> dict | None:
    '''Publishes incidents for an operator, sending a message to all subscribers.'''
    subject = f"New incident for {operator_code}"

    default_message = f'''The following incident/s has been reported for {
        operator_code}:\n\n'''

    sms_message = ""

    email_message = f"""The following incident/s has been reported for {
        operator_code}:\n\n"""

    for incident in incidents_list:
        if not all(key in incident for key in ['summary',
                                               'start_time',
                                               'end_time',
                                               'uri',
                                               'routes_affected']):
            continue

        incident_summary = incident['summary']
        incident_start = transform_datetime_string(incident['start_time'])
        incident_end = transform_datetime_string(incident['end_time'])
        incident_routes = incident['routes_affected']
        incident_uri = incident['uri']

        incident_detail = f"""
Summary: {incident_summary}\n
Start Date: {incident_start}\n
End Date: {incident_end}\n
"""
        routes = f"Routes Affected: {incident_routes}\n"
        detail_with_link = f"Link to the above incident: {incident_uri}\n\n"

        default_message += incident_detail + detail_with_link
        sms_message += incident_detail + detail_with_link
        email_message += incident_detail + routes + detail_with_link

    try:
        response = publish_multi_message(
            sns_client,
            topic_arn,
            subject,
            default_message,
            sms_message,
            email_message
        )
        return response
    except NoCredentialsError:
        logging.error("Error: No AWS credentials found.")
    except PartialCredentialsError:
        logging.error("Error: Incomplete AWS credentials.")
    except Exception as e:
        logging.error("An error occurred: %s", e)
    return None


def get_affected_incidents(op_code: str, incidents_list: list[dict]) -> list[dict]:
    '''Returns a list of incidents that have the operator code in their dictionary'''
    affected_incidents = []
    for incident in incidents_list:
        if op_code in incident['operator_codes']:
            affected_incidents.append(incident)
    return [incident for incident in incidents_list if op_code in incident['operator_codes']]


def send_message(incidents: list[dict]) -> None:
    '''Send a message to all subscribers to any topic if an operator is affected by an incident'''
    sns = get_sns_client()
    topics = get_topics_arns_from_aws(sns)
    subscribed_topics = filter_topics(FILTER_TOPICS_BY, topics)
    operator_arn_list = extract_operator_to_dictionary(subscribed_topics)
    operator_list = [
        topic['shortcode'] for topic in operator_arn_list]
    logging.info("\nTrain operators in AWS: %s\n", operator_list)

    for operator in operator_arn_list:
        operator['incidents'] = get_affected_incidents(
            operator['shortcode'], incidents)

        if len(operator['incidents']) == 0:
            continue
        response = publish_list_to_topic(
            sns, operator['TopicArn'], operator['shortcode'], operator['incidents'])
        logging.info("Response: %s", response)
