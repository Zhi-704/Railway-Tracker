""" Unit tests to test load PDF functions. """

import unittest
from unittest.mock import MagicMock, patch
from os import environ

from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor

from extract_pdf import (
    get_connection,
    get_cursor,
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
class TestExtractPdf(unittest.TestCase):
    """ Tests for loading PDF into email attachment and to S3 bucket. """

    @patch("extract_pdf.connect")
    def test_get_connection(self, mock_connect: connection):
        """ Tests get_connection returns connection. """

        mock_connect.return_value = "mock_connection"
        db_connection = get_connection()

        self.assertEqual(db_connection, "mock_connection")
        mock_connect.assert_called_once()

    @patch("extract_pdf.get_connection")
    def test_get_cursor(self, mock_get_connection: connection):
        """ Tests get_cursor returns cursor. """

        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        db_cursor = get_cursor(mock_connection)

        mock_connection.cursor.assert_called_once_with(
            cursor_factory=RealDictCursor)
        self.assertEqual(db_cursor, mock_connection.cursor())
