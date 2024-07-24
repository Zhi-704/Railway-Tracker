""" Unit tests to test archive functions. """
from psycopg2.extensions import connection, cursor
import psycopg2
from db_connection import get_connection, get_cursor, execute
import db_connection
import unittest
import os
from unittest.mock import MagicMock, patch
from clean_national_rail import clean_national_rail_incidents

from clean_real_time_trains import (
    get_all_station_ids,
    get_month_old_waypoints
)


class ArchiveTests(unittest.TestCase):
    """ Class for testing functions from the archive directory. """

    def setUp(self):

        incidents = {
            'incident_id': '1',
            'incident_number': '1',
            'creation_time': '',
            'incident_start': '',
            'incident_end': '',
            'is_planned': True,
            'incident_summary': "incident summary",
            'incident_description': 'incident description',
            'incident_uri': 'uri',
            'affected_routes': 'routes'
        }

    @patch.dict(
        os.environ,
        {
            "DB_IP": "localhost",
            "DB_NAME": "test_db",
            "DB_USERNAME": "test_username",
            "DB_PASSWORD": "test_password",
            "DB_PORT": "test_port",
        },
    )
    @patch("db_connection.connect")
    @patch("db_connection.load_dotenv")
    def test_get_connection(self, mock_load_dotenv, mock_connect: connection):
        """ Tests get_connection returns connection. """

        mock_connect.return_value = "mock_connection"
        db_connection = get_connection()

        assert db_connection == "mock_connection"
        mock_load_dotenv.assert_called_once()
        mock_connect.assert_called_once()

    @patch("db_connection.get_connection")
    def test_get_cursor(self, mock_get_connection: connection):
        """ Tests get_cursor returns cursor. """

        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection
        db_cursor = get_cursor(mock_connection)

        mock_connection.cursor.assert_called_once_with(
            cursor_factory=psycopg2.extras.RealDictCursor)
        self.assertIsNotNone(db_cursor)
        assert db_cursor == mock_connection.cursor()

    # Replace with actual connect function
    @patch('db_connection.get_connection')
    @patch("db_connection.get_cursor")
    def test_execute_success(self, mock_get_connection, mock_get_cursor):

        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection

        mock_cursor = MagicMock()
        mock_get_cursor.return_value = mock_cursor

        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = True
        mock_cursor.fetchall.return_value = [{'data': 'value'}]

        result = db_connection.execute(
            mock_connection, "SELECT * FROM station", ())

        self.assertIsNotNone(result, "The result should not be None")

    @patch('db_connection.get_connection')
    def test_get_all_station_ids(self, mock_get_connection):

        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection

        result = get_all_station_ids(mock_connection)

        self.assertIsNotNone(result, "The result should not be None")

    @patch('db_connection.get_connection')
    def test_get_month_old_waypoints(self, mock_get_connection):

        mock_connection = MagicMock()
        mock_get_connection.return_value = mock_connection

        result = get_month_old_waypoints(mock_connection, 1)

        self.assertIsNotNone(result, "The result should not be None")
