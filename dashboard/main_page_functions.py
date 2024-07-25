"""
"""

import datetime as dt
from os import environ

from boto3 import client
from dotenv import load_dotenv
import streamlit as st
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor

load_dotenv()
FETCH_TYPES = ["all", "one", "many"]


def get_db_connection() -> connection | None:
    """return a database connection"""
    try:
        return connect(
            host=environ['DB_HOST'],
            dbname=environ['DB_NAME'],
            user=environ['DB_USERNAME'],
            password=environ['DB_PASSWORD'],
            port=environ['DB_PORT']
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        st.write(e)
        return None


def get_db_cursor(conn: connection) -> cursor | None:
    """return a cursor object based on a given connection"""
    try:
        return conn.cursor(cursor_factory=RealDictCursor)
    except Exception as e:  # pylint: disable=broad-exception-caught
        st.write(e)
        return None


def run_fetch_command(curs: cursor, fetch_amount):
    """"""
    match(fetch_amount):
        case "all":
            return curs.fetchall()
        case "many":
            return curs.fetchmany()
        case "one":
            return curs.fetchone()
        case _:
            return None


def fetch_from_query(fetch_amount: str, query: str):
    """"""
    try:
        if fetch_amount not in FETCH_TYPES:
            raise ValueError
        conn = get_db_connection()
        with get_db_cursor(conn) as curs:
            curs.execute(query)
            match(fetch_amount):
                case "all":
                    res = curs.fetchall()
                case "many":
                    res = curs.fetchmany()
                case "one":
                    res = curs.fetchone()
                case _:
                    raise ValueError
            conn.close()
        return res
    except Exception as e:
        st.error(e)
        return None


def convert_datetime_to_string(input_date: dt.datetime) -> str:
    """take a datetime object and return an appropriate formatted string."""
    try:
        return dt.datetime.strftime(input_date, "%d/%m/%Y")
    except ValueError:
        return ""


def get_date_range_query(time_range, date_metric: str) -> str:
    """return a single line that can be added to a postgres query.
    this will help filter data by a time range."""
    if not (time_range and date_metric):
        return ""
    return f"WHERE {date_metric} >= NOW() - interval '{time_range}'"


def get_closest_scheduled_incident() -> str | None:
    """return the information on the closest incident scheduled
    after the current time."""
    query = """
    SELECT incident_summary, incident_start
    FROM incident WHERE incident_start >= CURRENT_DATE
    ORDER BY incident_start
    """
    res = fetch_from_query("one", query)
    if res:
        return f"[ {convert_datetime_to_string(res["incident_start"])} ] {res["incident_summary"]}"
    return None


def get_total_delays_for_every_station(date_range: str):
    """"""
    date_range_query = get_date_range_query(date_range, "w.actual_arrival")
    query = f"""
    SELECT
    s.station_name,
    ROUND(SUM(EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) +
    EXTRACT(EPOCH FROM (actual_departure - booked_departure))) / 60, 2) AS total_delay_minutes
    FROM waypoint w
    JOIN station s ON w.station_id = s.station_id
    {date_range_query}
    GROUP BY s.station_id, s.station_name
    ORDER BY total_delay_minutes DESC;
    """
    res = fetch_from_query("all", query)
    return res


def get_station_with_highest_delay(date_range: str):
    """get station with highest delay in seconds"""
    date_range_query = get_date_range_query(
        date_range, date_metric="w.actual_arrival")
    query = f"""
    SELECT
    s.station_name,
    ROUND(SUM(EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) +
    EXTRACT(EPOCH FROM (actual_departure - booked_departure))) / 60, 2) AS total_delay_minutes
    FROM waypoint w
    JOIN station s ON w.station_id = s.station_id
    {date_range_query}
    GROUP BY s.station_id, s.station_name
    ORDER BY total_delay_minutes DESC;
    """

    res = fetch_from_query("one", query)
    return f"{res["station_name"]}: total delays of {res["total_delay_minutes"]} minutes"


def get_trains_cancelled_per_station_percentage():
    """"""
    query = """
    WITH total_trains AS (
        SELECT w.station_id, COUNT(*) AS total_count
        FROM waypoint w
        GROUP BY w.station_id
    ),
    cancelled_trains AS (
        SELECT w.station_id, COUNT(*) AS cancelled_count
        FROM waypoint w
        JOIN cancellation c ON w.waypoint_id = c.waypoint_id 
        GROUP BY w.station_id
    )
    SELECT
        t.station_id,
        s.station_crs,
        s.station_name,
        c.cancelled_count,
        t.total_count,
        CASE
            WHEN t.total_count = 0 THEN 0
            ELSE ROUND((c.cancelled_count * 100.0 / t.total_count), 2)
        END AS cancellation_percentage
    FROM total_trains t
    JOIN cancelled_trains c ON t.station_id = c.station_id
    JOIN  station s ON t.station_id = s.station_id;
    """
    res = fetch_from_query("all", query)
    return res


def get_average_delays_all():
    """"""
    query = """
    SELECT
    s.station_name,
    ROUND(AVG(EXTRACT(EPOCH FROM (w.actual_arrival - w.booked_arrival)) / 60), 2) AS avg_arrival_delay_minutes,
    ROUND(AVG(EXTRACT(EPOCH FROM (w.actual_departure - w.booked_departure)) / 60), 2) AS avg_departure_delay_minutes
    FROM waypoint w
    JOIN station s ON s.station_id=w.station_id
    GROUP BY s.station_id;
    """

    res = fetch_from_query("all", query)
    return res


def get_average_delays_over_a_minute():
    query = """
    SELECT 
    s.station_name,
    ROUND(AVG( EXTRACT(EPOCH FROM (w.actual_arrival - w.booked_arrival)) / 60), 2) 
    AS avg_overall_delay_minutes
    FROM waypoint w
    JOIN station s ON s.station_id=w.station_id
    WHERE EXTRACT(EPOCH FROM (w.actual_arrival - w.booked_arrival)) / 60 > 1
    GROUP BY s.station_name;
    """
    res = fetch_from_query("all", query)
    return res
