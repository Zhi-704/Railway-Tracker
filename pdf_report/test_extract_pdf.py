from unittest.mock import patch, MagicMock

import pytest

from extract_pdf import get_connection, get_cursor, query_db, extract_pdf


@pytest.fixture
def mock_connection():
    """Fixture to mock database connection."""
    with patch('extract_pdf.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        yield mock_conn


@pytest.fixture
def mock_cursor(mock_connection):
    """Fixture to mock database cursor."""
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    yield mock_cursor


def test_get_connection(mock_connection):
    """Test the get_connection function."""
    with patch('extract_pdf.load_dotenv') as mock_load_dotenv:
        conn = get_connection()
        mock_load_dotenv.assert_called_once()
        assert conn == mock_connection
        mock_connection.cursor.assert_not_called()


def test_get_cursor(mock_cursor):
    """Test the get_cursor function."""
    with patch('extract_pdf.get_connection') as mock_get_connection:
        mock_conn = MagicMock()
        mock_get_connection.return_value = mock_conn
        cur = get_cursor(mock_conn)
        assert cur == mock_cursor
        mock_conn.cursor.assert_called_once_with(cursor_factory=MagicMock)


def test_query_db(mock_cursor):
    """Test the query_db function."""
    mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'Test'}]
    conn = MagicMock()
    query = "SELECT * FROM waypoint JOIN station USING (station_id)"
    data = query_db(conn, query)
    mock_cursor.execute.assert_called_once_with(query)
    assert data == [{'id': 1, 'name': 'Test'}]


@patch('extract_pdf.query_db')
def test_extract_pdf(mock_query_db):
    """Test the extract_pdf function."""
    mock_query_db.return_value = [{'id': 1, 'name': 'Test'}]
    data = extract_pdf()
    expected_query = """SELECT * FROM waypoint JOIN station USING (station_id)"""
    mock_query_db.assert_called_once_with(MagicMock(), expected_query)
    assert data == [{'id': 1, 'name': 'Test'}]
