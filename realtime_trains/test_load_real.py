'''Test file for the python file load'''

from unittest.mock import MagicMock, patch
import unittest

from load import (
    get_id_if_exists,
    insert_or_get_waypoint,
    insert_or_get_entry,
    import_to_database
)


class TestGetIdIfExists(unittest.TestCase):
    '''Class for testing the function get_id_if_exists'''

    def setUp(self):
        '''Set up variables to be used for every tests'''
        self.cur = MagicMock()
        self.table_name = 'test_table'
        self.conditions = {'name': 'TestName', 'status': None}

    def test_get_id_if_exists_found(self):
        '''Test for case an id is returned'''
        self.cur.fetchone.return_value = (1,)

        result = get_id_if_exists(self.cur, self.table_name, self.conditions)

        assert result == 1

    def test_get_id_if_exists_not_found(self):
        '''Test for case where an id is not found'''
        self.cur.fetchone.return_value = None

        result = get_id_if_exists(self.cur, self.table_name, self.conditions)

        assert result is None


class TestInsertOrGetEntry(unittest.TestCase):
    '''Class for testing the function insert_or_get_entry'''

    def setUp(self):
        '''Set up variables to be used for every tests'''
        self.table_name = 'test_table'
        self.insert_values = {'name': 'TestName', 'status': 'active'}
        self.unique_data_conditions = {'name': 'TestName'}
        self.entry_name = 'test_entry'

        self.conn = MagicMock()
        self.cur = MagicMock()

    @patch('load.get_id_if_exists')
    def test_insert_or_get_entry_existing(self, mock_get_id_if_exists):
        '''Test for case if there exists an entry in the database'''
        mock_get_id_if_exists.return_value = 1

        result = insert_or_get_entry(
            self.table_name,
            self.insert_values,
            self.unique_data_conditions,
            self.entry_name,
            self.conn,
            self.cur
        )

        assert result == 1
        assert self.cur.execute.call_count == 0
        assert self.conn.commit.call_count == 0
        assert self.conn.rollback.call_count == 0

    @patch('load.get_id_if_exists')
    def test_insert_or_get_entry_insert(self, mock_get_id_if_exists):
        '''Test for case if there exists no entry in the database'''
        mock_get_id_if_exists.return_value = None

        self.cur.fetchone.return_value = (2,)

        result = insert_or_get_entry(
            self.table_name,
            self.insert_values,
            self.unique_data_conditions,
            self.entry_name,
            self.conn,
            self.cur
        )

        expected_columns = 'name, status'
        expected_num_of_values = '%s, %s'
        expected_query = f'''
        INSERT INTO {self.table_name} ({expected_columns})
        VALUES
        ({expected_num_of_values})
        RETURNING {self.table_name}_id
        '''
        expected_values = ('TestName', 'active')

        assert result == 2
        self.cur.execute.assert_called_once_with(
            expected_query, expected_values)
        assert self.conn.commit.call_count == 1
        assert self.conn.rollback.call_count == 0

    @patch('load.get_id_if_exists')
    def test_insert_or_get_entry_error(self, mock_get_id_if_exists):
        '''Test for case where the query is incorrect'''
        mock_get_id_if_exists.return_value = None

        self.cur.execute.side_effect = Exception("Database error")

        result = insert_or_get_entry(
            self.table_name,
            self.insert_values,
            self.unique_data_conditions,
            self.entry_name,
            self.conn,
            self.cur
        )

        expected_columns = 'name, status'
        expected_num_of_values = '%s, %s'
        expected_query = f'''
        INSERT INTO {self.table_name} ({expected_columns})
        VALUES
        ({expected_num_of_values})
        RETURNING {self.table_name}_id
        '''
        expected_values = ('TestName', 'active')

        assert result is None
        self.cur.execute.assert_called_once_with(
            expected_query, expected_values)
        assert self.conn.commit.call_count == 0
        assert self.conn.rollback.call_count == 1


class TestImportToDatabase(unittest.TestCase):
    '''Class for testing the function import_to_database'''

    def setUp(self):
        '''Set up variables to be used for every tests'''
        self.stations = [
            {
                'location': {'crs': 'STN1', 'name': 'Station 1'},
                'services': [
                    {
                        'id': 101,
                        'operator': 'Op1',
                        'locationDetail': {'detail': 'A', 'cancelReasonCode': 'C1'}
                    }
                ]
            }
        ]

    @patch('load.get_connection')
    @patch('load.get_cursor')
    @patch('load.insert_or_get_station')
    @patch('load.insert_or_get_operator')
    @patch('load.insert_or_get_service')
    @patch('load.insert_or_get_waypoint')
    @patch('load.insert_or_get_cancel_code')
    @patch('load.insert_or_get_cancellation')
    def test_import_to_database(self,
                                mock_insert_or_get_cancellation,
                                mock_insert_or_get_cancel_code,
                                mock_insert_or_get_waypoint,
                                mock_insert_or_get_service,
                                mock_insert_or_get_operator,
                                mock_insert_or_get_station,
                                mock_get_cursor,
                                mock_get_connection):
        '''Checks for base case with the functions called the expected amount of times'''
        mock_conn = MagicMock()
        mock_cur = MagicMock()

        mock_get_connection.return_value = mock_conn
        mock_get_cursor.return_value = mock_cur
        mock_insert_or_get_station.return_value = 1
        mock_insert_or_get_operator.return_value = 2
        mock_insert_or_get_service.return_value = 3
        mock_insert_or_get_waypoint.return_value = 4
        mock_insert_or_get_cancel_code.return_value = 5
        mock_insert_or_get_cancellation.return_value = None

        import_to_database(self.stations)

        mock_get_connection.assert_called_once()
        mock_get_cursor.assert_called_once_with(mock_conn)
        mock_insert_or_get_station.assert_called_once_with(
            self.stations[0]['location'], mock_conn, mock_cur)
        mock_insert_or_get_operator.assert_called_once_with(
            self.stations[0]['services'][0], mock_conn, mock_cur)
        mock_insert_or_get_service.assert_called_once_with(
            self.stations[0]['services'][0], 2, mock_conn, mock_cur)
        mock_insert_or_get_waypoint.assert_called_once_with(
            1, 3, self.stations[0]['services'][0], mock_conn, mock_cur)
        mock_insert_or_get_cancel_code.assert_called_once_with(
            self.stations[0]['services'][0]['locationDetail'], mock_conn, mock_cur)
        mock_insert_or_get_cancellation.assert_called_once_with(
            5, 4, mock_conn, mock_cur)

        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()


class TestInsertOrGetWaypoint(unittest.TestCase):
    '''Class for testing the function insert_or_get_waypoint'''

    def setUp(self):
        '''Set up variables to be used for every tests'''

        self.station_id = 1
        self.service_id = 2
        self.service_dict = {
            "locationDetail": {
                "gbttBookedArrival": "1230",
                "realtimeArrival": "1235",
                "gbttBookedDeparture": "1300",
                "realtimeDeparture": "1305",
                "gbttBookedArrivalNextDay": False,
                "realtimeArrivalNextDay": False,
                "gbttBookedDepartureNextDay": False,
                "realtimeDepartureNextDay": False
            },
            "runDate": "2024-07-21"
        }
        self.conn = MagicMock()
        self.cur = MagicMock()

    @patch('load.get_id_if_exists')
    def test_insert_or_get_waypoint_existing(self, mock_get_id_if_exists):
        '''Test for case if there exists a waypoint entry in the database'''

        mock_get_id_if_exists.return_value = 1

        result = insert_or_get_waypoint(
            self.station_id,
            self.service_id,
            self.service_dict,
            self.conn,
            self.cur
        )

        self.assertEqual(result, 1)
        self.cur.execute.assert_not_called()
        self.conn.commit.assert_not_called()
        self.conn.rollback.assert_not_called()

    @patch('load.get_id_if_exists')
    def test_insert_or_get_waypoint_insert(self, mock_get_id_if_exists):
        '''Test for case if there is no same existing waypoint entry in the database'''

        mock_get_id_if_exists.return_value = None

        self.cur.fetchone.return_value = (2,)

        result = insert_or_get_waypoint(
            self.station_id,
            self.service_id,
            self.service_dict,
            self.conn,
            self.cur
        )

        self.assertEqual(result, 2)
        self.conn.commit.assert_called_once()
        self.conn.rollback.assert_not_called()

    @patch('load.get_id_if_exists')
    def test_insert_or_get_waypoint_error(self, mock_get_id_if_exists):
        '''Test for case if there is an exception when executing the query'''
        mock_get_id_if_exists.return_value = None

        self.cur.execute.side_effect = Exception

        result = insert_or_get_waypoint(
            self.station_id,
            self.service_id,
            self.service_dict,
            self.conn,
            self.cur
        )

        self.assertIsNone(result)

        self.conn.commit.assert_not_called()
        self.conn.rollback.assert_called_once()
