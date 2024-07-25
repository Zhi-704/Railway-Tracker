""" Unit tests to test load PDF functions. """

import unittest
from unittest.mock import MagicMock, patch
from os import environ
from io import BytesIO
from datetime import datetime
from email.mime.multipart import MIMEMultipart

from botocore.exceptions import ClientError
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor

from load_pdf import (
    get_connection,
    get_cursor,
    get_subscribers,
    create_ses_client,
    send_email,
    get_s3_client,
    upload_pdf_data_to_s3
)


@patch.dict(
    environ,
    {
        "DB_IP": "localhost",
        "DB_NAME": "test_db",
        "DB_USERNAME": "test_username",
        "DB_PASSWORD": "test_password",
        "DB_PORT": "test_port",
        "AWS_ACCESS_KEY": 'fake_access_key',
        'AWS_SECRET_KEY': 'fake_secret_key'
    },
)
class TestLoadPdf(unittest.TestCase):
    """ Tests for loading PDF into email attachment and to S3 bucket. """

    @patch("load_pdf.connect")
    def test_get_connection(self, mock_connect: connection):
        """ Tests get_connection returns connection. """

        mock_connect.return_value = "mock_connection"
        db_connection = get_connection()

        self.assertEqual(db_connection, "mock_connection")
        mock_connect.assert_called_once()

    @patch("load_pdf.get_connection")
    def test_get_cursor(self, mock_get_connection: connection):
        """ Tests get_cursor returns cursor. """

        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        db_cursor = get_cursor(mock_connection)

        mock_connection.cursor.assert_called_once_with(
            cursor_factory=psycopg2.extras.RealDictCursor)
        self.assertEqual(db_cursor, mock_connection.cursor())

    @patch('load_pdf.get_cursor')
    def test_successful_get_subscribers(self, mock_get_cursor):

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {'email': 'test1@example.com'}, {'email': 'test2@example.com'}]
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        conn = MagicMock()
        result = get_subscribers(conn)

        self.assertEqual(result, ['test1@example.com', 'test2@example.com'])
        mock_cursor.execute.assert_called_once_with(
            "SELECT email FROM subscriber;")
        mock_cursor.fetchall.assert_called_once()

    @patch('load_pdf.client')
    @patch('load_pdf.environ', {'AWS_ACCESS_KEY': 'fake_access_key', 'AWS_SECRET_KEY': 'fake_secret_key'})
    def test_successful_ses_client_creation(self, mock_boto_client):

        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        result = create_ses_client()

        self.assertEqual(result, mock_client)
        mock_boto_client.assert_called_once_with(
            "ses",
            region_name="eu-west-2",
            aws_access_key_id='fake_access_key',
            aws_secret_access_key='fake_secret_key'
        )

    @patch('load_pdf.client')
    @patch('load_pdf.environ', {'AWS_ACCESS_KEY': 'fake_access_key', 'AWS_SECRET_KEY': 'fake_secret_key'})
    def test_create_ses_client_failure(self, mock_boto_client):

        mock_boto_client.side_effect = ClientError(
            {"Error": {"Code": "InvalidClientTokenId",
                       "Message": "The security token included in the request is invalid"}},
            "CreateClient"
        )

        with self.assertRaises(RuntimeError) as context_manager:
            create_ses_client()

        self.assertIn(
            "Error creating SES client: An error occurred (InvalidClientTokenId)", str(context_manager.exception))

    def test_successful_email_send(self):
        mock_ses_client = MagicMock()
        mock_ses_client.send_raw_email.return_value = {
            "MessageId": "fake-message-id"}

        test_sender = "test@example.com"
        test_subscribers = ["subscriber1@example.com",
                            "subscriber2@example.com"]
        msg = MIMEMultipart()

        send_email(mock_ses_client, test_sender, test_subscribers, msg)

        calls = [
            unittest.mock.call(
                Source=test_sender,
                Destinations=[subscriber],
                RawMessage={"Data": msg.as_string()},
            ) for subscriber in test_subscribers
        ]
        mock_ses_client.send_raw_email.assert_has_calls(calls)

    @patch('load_pdf.client')
    @patch('load_pdf.environ', {'AWS_ACCESS_KEY': 'fake_access_key', 'AWS_SECRET_KEY': 'fake_secret_key'})
    def test_successful_s3_client_creation(self, mock_boto_client):

        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        result = get_s3_client()

        self.assertEqual(result, mock_client)
        mock_boto_client.assert_called_once_with(
            's3',
            aws_access_key_id='fake_access_key',
            aws_secret_access_key='fake_secret_key')

    def test_pdf_upload_to_s3_successful(self):
        mock_s3_client = MagicMock()
        bucket_name = 'test-bucket'
        s3_filename = 'test.pdf'
        pdf_content = BytesIO(b"Fake PDF content")

        upload_pdf_data_to_s3(mock_s3_client, bucket_name,
                              s3_filename, pdf_content)

        mock_s3_client.upload_fileobj.assert_called_once_with(
            pdf_content, bucket_name, s3_filename)
