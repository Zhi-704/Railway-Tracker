""" Unit tests to test archive functions. """
from psycopg2.extensions import connection, cursor
import psycopg2
from db_connection import get_connection, get_cursor, execute
import db_connection
import unittest
import os
from unittest.mock import MagicMock, patch

from clean_real_time_trains import (
    get_all_station_ids,
    get_month_old_waypoints,
    compute_avg_delay_for_station,
    compute_cancellation_count_for_station,
    insert_performance_archive,
    delete_cancellation,
    delete_waypoint,
    get_table_size
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

    # @patch('db_connection.get_connection')
    @patch("db_connection.get_cursor")
    def test_execute_success(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('row1',), ('row2',)]
        mock_conn = MagicMock()
        test_query = "SELECT * FROM table"

        result = execute(mock_conn, test_query, ())

        mock_get_cursor.assert_called_once_with(mock_conn)
        mock_cursor.execute.assert_called_once_with(
            'SELECT * FROM table', ())
        mock_cursor.fetchall.assert_called_once()
        self.assertEqual(result, [('row1',), ('row2',)])

    @patch("db_connection.get_cursor")
    def test_get_station_ids(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'station_id': 1}, {'station_id': 2}]
        mock_conn = MagicMock()

        result = get_all_station_ids(mock_conn)

        mock_get_cursor.assert_called_once_with(mock_conn)
        mock_cursor.execute.assert_called_once_with("""
        SELECT station_id
        FROM station;
    """, ())
        mock_cursor.fetchall.assert_called_once()
        self.assertEqual(result, [{'station_id': 1}, {'station_id': 2}])

    @patch("db_connection.get_cursor")
    def test_get_month_old_waypoints(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'waypoint': 1}, {'waypoint': 2}]
        mock_conn = MagicMock()

        result = get_month_old_waypoints(mock_conn, 1)

        mock_get_cursor.assert_called_once_with(mock_conn)
        mock_cursor.execute.assert_called_once_with("""
        SELECT *
        FROM waypoint
        WHERE run_date <= CURRENT_DATE - INTERVAL '1 month'
            AND station_id = %s;
    """, (1,))
        mock_cursor.fetchall.assert_called_once()
        self.assertEqual(result, [{'waypoint': 1}, {'waypoint': 2}])

    @patch("db_connection.get_cursor")
    def test_compute_avg_delay_for_station(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [{'avg_overall_delay': 1.0}]
        mock_conn = MagicMock()

        result = compute_avg_delay_for_station(mock_conn, 1)

        mock_get_cursor.assert_called_once_with(mock_conn)
        mock_cursor.execute.assert_called_once_with("""
        SELECT
            station_id,
            AVG((actual_arrival - booked_arrival)+(actual_departure - booked_departure))avg_overall_delay
        FROM waypoint
        WHERE station_id = %s
            AND run_date <= CURRENT_DATE - INTERVAL '1 month'
        GROUP BY station_id;
    """, (1,))
        mock_cursor.fetchall.assert_called_once()
        self.assertEqual(result, 1.0)

    @patch("db_connection.get_cursor")
    def test_compute_cancellation_count_for_station(self, mock_get_cursor):
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [{'cancellation_count': 1}]
        mock_conn = MagicMock()

        result = compute_cancellation_count_for_station(mock_conn, 1)

        mock_get_cursor.assert_called_once_with(mock_conn)
        mock_cursor.execute.assert_called_once_with("""
        SELECT COUNT(cancellation_id) AS cancellation_count
        FROM waypoint w
        JOIN cancellation c
        ON c.waypoint_id = w.waypoint_id
        WHERE w.station_id = %s
            AND run_date <= CURRENT_DATE - INTERVAL '1 month';
    """, (1,))
        mock_cursor.fetchall.assert_called_once()
        self.assertEqual(result, 1)

    @patch("db_connection.get_cursor")
    def test_insert_performance_archive(self, mock_get_cursor):

        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn = MagicMock()

        archive_data = {
            "station_id": 1,
            "avg_delay": 5.5,
            "cancellation_count": 2
        }
        result = insert_performance_archive(mock_conn, archive_data)

        mock_get_cursor.assert_called_once_with(mock_conn)
        mock_cursor.execute.assert_called_once_with("""
        INSERT INTO performance_archive (station_id, avg_delay, cancellation_count, creation_date)
        VALUES (%s, %s, %s, TIMEZONE('Europe/London', CURRENT_TIMESTAMP));
    """, (archive_data["station_id"], archive_data["avg_delay"], archive_data["cancellation_count"]))

        mock_cursor.fetchall.assert_called_once()
        self.assertEqual(result, None)

    @patch("db_connection.get_cursor")
    def test_delete_cancellation(self, mock_get_cursor):

        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn = MagicMock()

        result = delete_cancellation(mock_conn, 0)

        mock_get_cursor.assert_called_once_with(mock_conn)
        mock_cursor.execute.assert_called_once_with("""
        DELETE FROM cancellation 
        WHERE waypoint_id = %s;
    """, (0,))

        mock_cursor.fetchall.assert_called_once()
        self.assertEqual(result, None)

    @patch("db_connection.get_cursor")
    def test_delete_waypoint(self, mock_get_cursor):

        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn = MagicMock()

        result = delete_waypoint(mock_conn, 0)

        mock_get_cursor.assert_called_once_with(mock_conn)
        mock_cursor.execute.assert_called_once_with("""
        DELETE FROM waypoint 
        WHERE waypoint_id = %s;
    """, (0,))

        mock_cursor.fetchall.assert_called_once()
        self.assertEqual(result, None)

    @patch("db_connection.get_cursor")
    def test_get_table_size(self, mock_get_cursor):

        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = 4
        mock_conn = MagicMock()

        result = get_table_size(mock_conn, 'test_table')

        mock_get_cursor.assert_called_once_with(mock_conn)
        mock_cursor.execute.assert_called_once_with("""
        SELECT COUNT(*) FROM test_table;
    """, ())

        mock_cursor.fetchall.assert_called_once()
        self.assertEqual(result, 4)
