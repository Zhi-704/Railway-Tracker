""" Unit tests to test load functions. """

from unittest.mock import MagicMock, patch
import os
from datetime import datetime

import psycopg2
from psycopg2.extensions import connection, cursor

from load import (
    get_connection,
    get_cursor,
    upload_incident,
    check_if_exists,
    get_operator_code_id,
    upload_affected_operator,
)


@patch.dict(
    os.environ,
    {
        "DB_HOST": "localhost",
        "DB_NAME": "test_db",
        "DB_USER": "test_username",
        "DB_PASS": "test_password",
        "DB_PORT": "test_port",
    },
)
@patch("load.connect")
def test_get_connection(mock_connect: connection):
    """ Tests get_connection returns connection. """

    mock_connect.return_value = "mock_connection"
    db_connection = get_connection()

    assert db_connection == "mock_connection"
    mock_connect.assert_called_once()


@patch("load.get_connection")
def test_get_cursor(mock_get_connection: connection):
    """ Tests get_cursor returns cursor. """

    mock_connection = MagicMock()
    mock_get_connection.return_value = mock_connection
    db_cursor = get_cursor(mock_connection)

    mock_connection.cursor.assert_called_once_with(
        cursor_factory=psycopg2.extras.RealDictCursor)
    assert db_cursor == mock_connection.cursor()


@patch("load.get_connection")
@patch("load.get_cursor")
def test_upload_incident(mock_get_cursor: cursor, mock_get_connection: connection):
    """ Tests uploading incidents and returning incident id."""

    mock_cursor = MagicMock()
    mock_get_cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [{'incident_id': 1}]

    mock_date = datetime.now()

    incident_mock = {
        "incident_number": "GUDIA665MOCK",
        "creation_time": mock_date,
        "start_time": mock_date,
        "end_time": mock_date,
        "is_planned": True,
        "summary": "mock incident summary",
        "description": "mock incident description",
        "uri": "www.incident.com",
        "routes_affected": "routes affected are x, y, z"
    }

    incident_id = upload_incident(mock_get_connection, incident_mock)
    assert incident_id == 1
    mock_cursor.execute.assert_called_with(
        """
        INSERT INTO incident (incident_number, creation_time, incident_start, incident_end, is_planned, incident_summary,
            incident_description, incident_uri, affected_routes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
        RETURNING incident_id;
    """,
        (incident_mock["incident_number"],
         incident_mock["creation_time"],
         incident_mock["start_time"],
         incident_mock["end_time"],
         incident_mock["is_planned"],
         incident_mock["summary"],
         incident_mock["description"],
         incident_mock["uri"],
         incident_mock["routes_affected"]),)


@patch("load.get_connection")
@patch("load.get_cursor")
def test_check_if_exists(mock_get_cursor: cursor, mock_get_connection: connection):
    """ Tests that checking if an entry in the database exists works as expected. """

    mock_cursor = MagicMock()
    mock_get_cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {'mock_table_id': 1}

    mock_table_name = 'mock_table'
    mock_conditions = {'mock_code': "XT"}

    operator_id = check_if_exists(mock_get_connection, mock_table_name,
                                  conditions=mock_conditions)

    assert operator_id == {'mock_table_id': 1}

    mock_cursor.execute.assert_called_with(
        'SELECT * FROM mock_table WHERE mock_code = %s', ('XT',),)


@patch("load.get_connection")
@patch("load.get_cursor")
def test_get_operator_code_id(mock_get_cursor: cursor, mock_get_connection: connection):
    """ Tests that getting an operator code id returns the id. """

    mock_cursor = MagicMock()
    mock_get_cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {'operator_id': 1}

    mock_operator_code = "XT"

    operator_id = get_operator_code_id(mock_get_connection, mock_operator_code)

    assert operator_id == 1


@patch("load.get_connection")
@patch("load.get_cursor")
def test_upload_affected_operator(mock_get_cursor: cursor, mock_get_connection: connection):
    """ Tests that uploading an affected operator for incidents inserts as expected. """

    mock_cursor = MagicMock()
    mock_get_cursor.return_value = mock_cursor

    mock_incident_id = 1
    mock_operator_id = 1

    upload_affected_operator(
        mock_get_connection, mock_incident_id, mock_operator_id)

    mock_cursor.execute.assert_called_with(
        """
        INSERT INTO affected_operator (incident_id, operator_id)
        VALUES (%s, %s)
        RETURNING affected_operator_id;
    """,
        (mock_incident_id, mock_operator_id),)
