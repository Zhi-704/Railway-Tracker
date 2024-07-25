""" Loads the PDF summary report of RealTimeTrains data into an S3 bucket. """

from os import environ, path
import logging

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from datetime import datetime

from dotenv import load_dotenv
from boto3 import client
from botocore.exceptions import NoCredentialsError, ClientError
from psycopg2 import connect, Error as psycopg2_error
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor


# REPORT_FILENAME = 'performance_report.pdf'


def get_s3_client() -> client:
    """ Returns s3 client. """
    try:
        return client('s3',
                      aws_access_key_id=environ['AWS_ACCESS_KEY'],
                      aws_secret_access_key=environ['AWS_SECRET_KEY'])
    except NoCredentialsError:
        logging.error("Error, no AWS credentials found")
        return None


def upload_pdf_to_s3(report_filename: str) -> None:
    """ Uploads a PDF file from local directory into S3 bucket. """
    s3 = get_s3_client()
    bucket = environ['S3_BUCKET_NAME']
    prefix = datetime.now()
    s3_file_name = f"{prefix}_{report_filename}"

    try:
        s3.upload_file(report_filename, bucket, s3_file_name)
        logging.info("Upload Successful: %s, to bucket: %s",
                     s3_file_name, bucket)
    except FileNotFoundError:
        logging.error("The file was not found.")
    except Exception:
        logging.error(
            "Error occurred when connecting and uploading to S3 bucket.")


def get_connection() -> connection:
    """ Retrieves connection and returns it. """

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


def get_subscribers(conn: connection) -> list:
    """ Queries the subscriber table, returning a list of all subscriber emails."""

    recipients = []
    try:
        with get_cursor(conn) as cur:
            cur.execute("SELECT email FROM subscriber;")
            subscribers = cur.fetchall()
            recipients = [subscriber['email'] for subscriber in subscribers]

    except psycopg2_error as e:
        logging.error("Error fetching subscribers: %s", e)

    return recipients


def create_ses_client() -> client:
    """ Creates and returns an SES client using AWS access keys."""

    try:
        return client(
            "ses",
            region_name="eu-west-2",
            aws_access_key_id=environ['AWS_ACCESS_KEY'],
            aws_secret_access_key=environ['AWS_SECRET_KEY']
        )
    except ClientError as e:
        raise RuntimeError(f"Error creating SES client: {e}") from e


def format_email(report_filename) -> None:
    """ Formats email with subject, body and attachment of PDF, and returns it. """

    body = "See the PDF document attached for insights into the performance of stations in the UK."
    sender = f"Railway Tracker <{environ['SOURCE_EMAIL']}>"

    msg = MIMEMultipart()
    msg["Subject"] = "Performance Report"
    msg["From"] = sender
    msg.attach(MIMEText(body, "html"))

    with open(report_filename, "rb") as attachment:
        part = MIMEApplication(attachment.read(), _subtype="pdf")
        part.add_header(
            "Content-Disposition", "attachment", filename=path.basename(report_filename)
        )
        msg.attach(part)

    return sender, msg


def send_email(ses_client: client, sender: str, subscribers: list[str], msg: MIMEMultipart) -> None:
    """ Sends PDF report as attachment in email to the verified email addresses in
        the subscribers list"""

    for subscriber in subscribers:
        try:
            response = ses_client.send_raw_email(
                Source=sender,
                Destinations=[subscriber],
                RawMessage={"Data": msg.as_string()},
            )
            logging.info(
                "Email sent to %s! Message ID: %s", subscribers, response["MessageId"]
            )
        except ClientError as e:
            logging.error(
                "Error sending email to %s: %s", subscribers, e.response["Error"]["Message"],
            )


def email_performance_report(report_filename: str) -> None:
    """ Main function to perform sending emails to subscribers:
        - Retrieves subscribers list from database.
        - Creates SES client to send email with.
        - Creates email and sends email. """

    subscribers = get_subscribers(get_connection())
    ses_client = create_ses_client()
    sender, message = format_email(report_filename)
    send_email(ses_client, sender, subscribers, message)


def load_pdf(report_filename: str) -> None:
    """ Sends the PDF of the performance report via email to subscribers
        Loads the PDF report to the s3 bucket with timestamp."""
    load_dotenv()
    email_performance_report(report_filename)
    upload_pdf_to_s3(report_filename)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    load_pdf()
