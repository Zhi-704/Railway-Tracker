'''Test file for the python file transform'''

from unittest.mock import patch

import pytest
from transform import (
    filter_keys,
    service_matches_criteria,
    process_station,
    process_all_stations
)


class TestFilterKeys:
    '''Class for testing the function filter_keys'''
    test_dict = {
        "a": 1,
        "b": 2,
        "c": 3,
        "d": 4,
        "e": 5
    }

    @pytest.mark.parametrize("keys, expected", [
        (["a"], {
            "b": 2,
            "c": 3,
            "d": 4,
            "e": 5
        }),
        (["b", "c"], {
            "a": 1,
            "d": 4,
            "e": 5
        }),
        ([], {
            "a": 1,
            "b": 2,
            "c": 3,
            "d": 4,
            "e": 5
        }),
        (["adsadasdasdsasda", "adsadsadas"], {
            "a": 1,
            "b": 2,
            "c": 3,
            "d": 4,
            "e": 5
        })
    ])
    def test_filters_keys(self, keys, expected):
        '''Test filtering dictionary function with expected output'''
        assert filter_keys(keys, self.test_dict.copy()) == expected
        with pytest.raises(TypeError):
            filter_keys(keys, [])


class TestServiceMatchesCriteria:
    '''Class for testing the function service_matches_criteria'''
    service = {
        "name": "ServiceA",
        "type": "Premium",
        "active": True,
        "region": "US"
    }

    @pytest.mark.parametrize("criteria, expected", [
        ({"name": "ServiceA"}, True),
        ({"name": "ServiceB"}, False),
        ({"type": "Premium", "active": True}, True),
        ({"type": "Basic"}, False),
        ({"region": "US"}, True),
        ({"region": "EU"}, False),
        ({}, True),
        ({"name": "ServiceA", "active": False}, False),
    ])
    def test_service_matches_criteria(self, criteria, expected):
        '''Test if service matches given criteria'''
        assert service_matches_criteria(self.service, criteria) == expected


class TestProcessStation():
    '''Class for testing the function process_station'''

    def test_process_station(self):
        '''Tests base case for processing station'''
        station_input = {
            'location': {'name': 'Test Station',
                         'code': 'TS',
                         'tiploc': 'remove',
                         'country': 'remove'},
            'services': [
                {'id': 1,
                 'serviceType': 'train',
                 'isPassenger': 'remove',
                 'locationDetail': {
                     'detail1': 'value1', 'origin': 'remove'}},
                {'id': 2,
                 'serviceType': 'bus',
                 'isPassenger': 'remove',
                 'locationDetail': {
                     'detail2': 'value2', 'origin': 'remove'}}
            ]
        }

        processed_station = {
            'location': {'name': 'Test Station', 'code': 'TS'},
            'services': [
                {'id': 1,
                 'serviceType': 'train',
                 'locationDetail': {
                     'detail1': 'value1'}}
            ]
        }

        result = process_station(station_input)

        assert result == processed_station

    def test_process_station_no_services_match(self):
        '''Tests case for when no services matches criteria'''

        station_input = {
            'location': {'name': 'Test Station',
                         'code': 'TS',
                         'tiploc': 'remove',
                         'country': 'remove'},
            'services': [
                {'id': 1,
                 'serviceType': 'bus',
                 'isPassenger': 'remove',
                 'locationDetail': {
                     'detail1': 'value1', 'origin': 'remove'}},
                {'id': 2,
                 'serviceType': 'bus',
                 'isPassenger': 'remove',
                 'locationDetail': {
                     'detail2': 'value2', 'origin': 'remove'}}
            ]
        }

        processed_station = {
            'location': {'name': 'Test Station', 'code': 'TS'},
            'services': [
            ]
        }

        result = process_station(station_input)

        assert result == processed_station

    def test_process_station_empty_services(self):
        '''Tests case for when there are no services'''

        station_input = {
            'location': {'name': 'Test Station',
                         'code': 'TS',
                         'tiploc': 'remove',
                         'country': 'remove'},
            'services': [
            ]
        }

        processed_station = {
            'location': {'name': 'Test Station', 'code': 'TS'},
            'services': [
            ]
        }

        result = process_station(station_input)

        assert result == processed_station


class TestProcessAllStations():
    '''Class for testing the function process_all_stations'''

    @patch('transform.process_station')
    def test_process_all_stations(self, mock_process_station):
        stations_data = [
            {'location': {'name': 'Station 1'}, 'services': []},
            {'location': {'name': 'Station 2'}, 'services': []}
        ]
        processed_data = [
            {'location': {'name': 'Station 1'}, 'services': []},
            {'location': {'name': 'Station 2'}, 'services': []}
        ]

        mock_process_station.side_effect = lambda station: station

        result = process_all_stations(stations_data)

        assert result == processed_data
        assert mock_process_station.call_count == 2

    @patch('transform.process_station')
    def test_process_all_stations_wrong_type(self, mock_process_station):
        stations_data = {'location': {'name': 'Station 1'}, 'services': []}
        processed_data = [
            {'location': {'name': 'Station 1'}, 'services': []},
            {'location': {'name': 'Station 2'}, 'services': []}
        ]

        mock_process_station.side_effect = lambda station: station

        with pytest.raises(TypeError):
            result = process_all_stations(stations_data)

        assert mock_process_station.call_count == 0
