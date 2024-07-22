'''Test file for the python file extract'''

import unittest
from unittest.mock import MagicMock, patch

from requests.exceptions import RequestException
from requests.auth import HTTPBasicAuth
from requests import Response

from extract_real import (
    get_data_from_api,
    get_yesterday_data_of_station,
    get_all_stations_crs,
    get_api_data_of_all_stations
)


class TestAPIFunctions(unittest.TestCase):
    '''Class for testing all api functions in the extract file'''

    @patch('extract_real.get')
    def test_get_data_from_api_success(self, mock_get):
        '''Test if api is called with the correct parameters'''
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 234
        mock_response.json.return_value = {'key': 'value'}
        mock_get.return_value = mock_response

        url = "http://example.com"
        username = "user"
        password = "pass"

        result = get_data_from_api(url, username, password)

        self.assertEqual(result, {'key': 'value'})
        mock_get.assert_called_once_with(
            url, auth=HTTPBasicAuth(username, password), timeout=10)
        mock_response.raise_for_status.assert_called_once()

    @patch('extract_real.get')
    def test_get_data_from_api_failure(self, mock_get):
        '''Test if scenario where the api request gives an exception'''

        mock_get.side_effect = RequestException("API error")

        url = 'http://example.com'
        username = 'user'
        password = 'pass'

        result = get_data_from_api(url, username, password)

        mock_get.assert_called_once_with(
            url, auth=HTTPBasicAuth(username, password), timeout=10)
        self.assertIsNone(result)

    @patch.dict('extract_real.ENV',
                {'REALTIME_USERNAME': 'user',
                 'REALTIME_PASSWORD': 'pass'})
    @patch('extract_real.get_api_url')
    @patch('extract_real.get_data_from_api')
    def test_get_yesterday_data_of_station_success(self,
                                                   mock_get_data_from_api,
                                                   mock_get_api_url):
        '''Test base case for retrieving API data of station'''
        mock_get_data_from_api.return_value = {'data': 'station_data'}
        mock_get_api_url.return_value = 'http://api.example.com'

        station_code = 'STN'
        result = get_yesterday_data_of_station(station_code)

        mock_get_api_url.assert_called_once()
        mock_get_data_from_api.assert_called_once()
        self.assertEqual(result, {'data': 'station_data'})

    @patch.dict('extract_real.ENV',
                {'REALTIME_USERNAME': 'user',
                 'REALTIME_PASSWORD': 'pass'})
    @patch('extract_real.get_api_url')
    @patch('extract_real.get_data_from_api')
    def test_get_yesterday_data_of_station_failure(self, mock_get_data_from_api, mock_get_api_url):
        '''Test case for retrieving API data of station where there is an error'''
        mock_get_data_from_api.return_value = None
        mock_get_api_url.return_value = 'http://api.example.com'

        station_code = 'STN'
        result = get_yesterday_data_of_station(station_code)

        mock_get_api_url.assert_called_once()
        mock_get_data_from_api.assert_called_once()
        self.assertIsNone(result)

    @patch('extract_real.get_connection')
    @patch('extract_real.get_cursor')
    def test_get_all_stations_crs(self, mock_get_cursor, mock_get_connection):
        '''Tests if the query matches the expected query'''
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [('STN1',), ('STN2',)]

        mock_get_connection.return_value = mock_conn
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = get_all_stations_crs()

        mock_get_connection.assert_called_once()
        mock_cursor.execute.assert_called_once_with(
            "SELECT station_crs FROM station")
        self.assertEqual(result, ['STN1', 'STN2'])

    @patch('extract_real.get_all_stations_crs')
    @patch('extract_real.get_yesterday_data_of_station')
    def test_get_api_data_of_all_stations(self,
                                          mock_get_yesterday_data_of_station,
                                          mock_get_all_stations_crs):
        '''Tests if the function calls functions an appropriate number of times'''
        mock_get_all_stations_crs.return_value = ['STN1', 'STN2']
        mock_get_yesterday_data_of_station.side_effect = [
            {'data': 'data1'}, {'data': 'data2'}]

        result = get_api_data_of_all_stations()

        mock_get_all_stations_crs.assert_called_once()
        self.assertEqual(mock_get_yesterday_data_of_station.call_count, 2)
        self.assertEqual(result, [{'data': 'data1'}, {'data': 'data2'}])
