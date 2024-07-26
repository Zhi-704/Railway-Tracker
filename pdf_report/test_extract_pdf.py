""" Unit tests to test load PDF functions. """

import unittest
from unittest.mock import MagicMock, patch
from os import environ

from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor

from extract_pdf import (
    get_connection,
    get_cursor,
    query_db
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

    @patch("extract_pdf.get_cursor")
    def test_query_success(self, mock_get_cursor):

        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('row1',), ('row2',)]
        mock_conn = MagicMock()
        test_query = "SELECT * FROM table"

        result = query_db(mock_conn, test_query)

        mock_get_cursor.assert_called_once_with(mock_conn)
        mock_cursor.execute.assert_called_once_with(test_query)
        mock_cursor.fetchall.assert_called_once()
        self.assertEqual(result, [('row1',), ('row2',)])
