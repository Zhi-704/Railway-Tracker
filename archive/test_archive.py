""" Unit tests to test archive functions. """
import unittest
from unittest.mock import patch
from clean_national_rail import clean_national_rail_incidents
from db_connection import get_connection, execute
from psycopg2.extensions import connection, cursor


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

    @patch("db_connection.connect")
    def test_clean_national_rail_incidents(self, mock_get_connection: connection):
        ...
