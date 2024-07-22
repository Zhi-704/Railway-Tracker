'''Script used for notifying all subscribed users of incidents for their operators.'''


from os import environ as ENV
import logging
from dotenv import load_dotenv

from boto3 import client
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


def get_latest_incidents(conn: connection,
                         item_type: str,
                         tag: str,
                         sales_limit: int,
                         sales_timeframe: str) -> list[dict]:
    '''Gets trending sales data'''

    query = f'''
SELECT
    T.{item_type}_id,
    T.title,
    A.name AS band,
    COUNT(DISTINCT TP.{item_type}_purchase_id) AS copies_sold,
    T.url
FROM {item_type}_purchase AS TP
JOIN {item_type} AS T ON TP.{item_type}_id = T.{item_type}_id
JOIN artist AS A ON T.artist_id = A.artist_id
JOIN {item_type}_tag_assignment AS TTA ON T.{item_type}_id = TTA.{item_type}_id
JOIN tag AS TG ON TTA.tag_id = TG.tag_id
WHERE TG.name = %s
AND TP.timestamp >= NOW() - INTERVAL '{sales_timeframe}'
GROUP BY
    T.{item_type}_id,
    T.title,
    A.name,
    T.url
HAVING COUNT(DISTINCT TP.{item_type}_purchase_id) >= %s
ORDER BY copies_sold DESC
'''

    try:
        with conn.cursor() as cur:
            cur.execute(query, (tag, sales_limit))
            trending = cur.fetchall()

        if len(trending) >= 1:
            return trending
    except Exception as e:
        logging.error(
            "Error fetching sales data for %s and tag %s: %s", item_type, tag, e)
        conn.rollback()

    return []


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


def extract_oeprator_code(topic_arn: str) -> str:
    '''Extracts the tag name from the topic arn'''
    if topic_arn is None or not isinstance(topic_arn, str):
        return None
    raw_tag = topic_arn.split(':')[-1]
    tag_parts = raw_tag.split('-')[2:]
    return ' '.join(tag_parts)


def extract_operator_to_dictionary(tags_list: list[dict]) -> list[dict]:
    '''Grabs the operator from list of arns'''
    for tag_arn in tags_list:
        topic_arn = tag_arn['TopicArn']
        tag_name = extract_oeprator_code(topic_arn)
        tag_arn['operator'] = tag_name
    return tags_list


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    load_dotenv()
    sns = get_sns_client()
    topics = get_topics_arns_from_aws(sns)
    subscribed_topics = filter_topics(FILTER_TOPICS_BY, topics)
    operator_list = extract_operator_to_dictionary(subscribed_topics)
    logging.info("\nTrain operators in AWS: %s\n", [
                 tag['operator'] for tag in operator_list])
    print(operator_list)
