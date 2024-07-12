from os import environ
import unittest
from unittest.mock import patch, mock_open
from extract import get_data_from_api


class TestExtract(unittest.TestCase):
    def setUp(self) -> None:
        self.api_key = "test_api_key"
        self.url = "https://api1.raildata.org.uk/1010-knowlegebase-incidents-xml-feed1_0/incidents.xml"
        self.headers = {
            "x-apikey": self.api_key,
            "User-Agent": ""
        }

    @patch('extract.get')
    @patch.dict(environ, {'APIKEY': 'test_api_key'})
    def test_get_data_from_api(self, mock_get) -> None:
        mock_response = mock_get.return_value
        mock_response.text = "Test response data"

        with mock_open() as mock_file:
            get_data_from_api()
            mock_file.assert_called_once_with(
                "data.xml", "w", encoding="utf-8")
            mock_file().write.assert_called_once_with("Test response data")

        mock_get.assert_called_once_with(
            self.url, headers=self.headers, timeout=10)

    @patch('extract.get')
    @patch.dict(environ, {'APIKEY': 'test_api_key'})
    def test_get_data_from_api_with_error(self, mock_get) -> None:
        mock_get.side_effect = Exception("Test exception")

        with self.assertRaises(Exception):
            get_data_from_api()
