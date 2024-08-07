"""
This file holds the query functions that are used in the main page
"""

import datetime as dt
from os import environ

from dotenv import load_dotenv
import streamlit as st
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor

load_dotenv()
FETCH_TYPES = ["all", "one"]

DATE_METRIC = "w.run_date"


def get_db_connection() -> connection | None:
    """return a database connection"""
    try:
        return connect(
            host=environ['DB_IP'],
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
    """fetch the results of a query execute using a cursor object and the size to fetch"""
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
    """execute a query given and return a result of a given size"""
    try:
        if fetch_amount not in FETCH_TYPES:
            raise ValueError
        conn = get_db_connection()
        with get_db_cursor(conn) as curs:
            curs.execute(query)
            match(fetch_amount):
                case "all":
                    res = curs.fetchall()
                case "one":
                    res = curs.fetchone()
                case _:
                    raise ValueError
            conn.close()
        return res
    except Exception as e:  # pylint: disable=broad-exception-caught
        st.error(e)
        return None


def convert_datetime_to_string(input_date: dt.datetime) -> str:
    """take a datetime object and return an appropriate formatted string."""
    try:
        return dt.datetime.strftime(input_date, "%d/%m/%Y")
    except ValueError:
        return ""


def get_date_range_query(time_range, is_join: bool = False) -> str:
    """return a single line that can be added to a postgres query.
    this will help filter data by a time range."""
    if not time_range:
        return ""
    if not is_join:
        return f"WHERE {DATE_METRIC} >= CURRENT_DATE - interval '{time_range}'"
    return f"HAVING {DATE_METRIC} >= CURRENT_DATE - interval '{time_range}'"


def get_closest_scheduled_incident() -> str | None:
    """return the information on the closest incident scheduled
    after the current time."""
    query = """
    SELECT incident_summary, incident_start
    FROM incident WHERE incident_start >= NOW()
    ORDER BY incident_start
    """
    res = fetch_from_query("one", query)
    if res:
        return f"[ {convert_datetime_to_string(res["incident_start"])} ] {res["incident_summary"]}"
    return None


def get_total_delays_for_every_station(date_range: str, time_group: str):
    """get the total delays for every station"""
    date_range_query = get_date_range_query(date_range)
    time_group_query = get_sum_for_range_query(time_group)
    query = f"""
    SELECT
    s.station_name,
    {time_group_query}
    FROM waypoint w
    JOIN station s ON w.station_id = s.station_id
    {date_range_query}
    GROUP BY s.station_id, s.station_name
    ORDER BY total_delay_minutes DESC;
    """
    res = fetch_from_query("all", query)
    return res


def get_sum_for_range_query(time_group: str) -> str:
    """get the sum of delays for a given time group, arrival, departure, or sum total"""
    res = """"""
    match time_group:
        case "arrival":
            return """ROUND(SUM(EXTRACT(EPOCH FROM(w.actual_arrival - w.booked_arrival)))/60, 2)
            AS total_delay_minutes"""
        case "departure":
            return """ROUND(SUM(EXTRACT(EPOCH FROM(w.actual_departure - w.booked_departure)))/60, 2)
            AS total_delay_minutes"""
        case "sum total":
            return """ROUND(SUM(EXTRACT(EPOCH FROM(w.actual_arrival - w.booked_arrival)) +
               EXTRACT(EPOCH FROM(w.actual_departure - w.booked_departure))) / 60, 2)
               AS total_delay_minutes"""
        case _:
            st.write("ERROR")

    return res


def get_avg_for_range_query(time_group: str) -> str:
    """get the avg of delays for a given time group, arrival, departure, or sum total"""
    res = """"""
    match time_group:
        case "arrival":
            return """ROUND(AVG(EXTRACT(EPOCH FROM(w.actual_arrival - w.booked_arrival)))/60, 2)
            AS total_delay_minutes"""
        case "departure":
            return """ROUND(AVG(EXTRACT(EPOCH FROM(w.actual_departure - w.booked_departure)))/60, 2)
            AS total_delay_minutes"""
        case "sum total":
            return """ROUND(AVG(EXTRACT(EPOCH FROM(w.actual_arrival - w.booked_arrival)) +
               EXTRACT(EPOCH FROM(w.actual_departure - w.booked_departure))) / 60, 2)
               AS total_delay_minutes"""
        case _:
            st.write("ERROR")

    return res


def get_station_with_highest_delay(date_range: str, time_group: str):
    """get the station with the highest delay in seconds"""
    date_range_query = get_date_range_query(date_range)

    time_group_query = get_sum_for_range_query(time_group)
    query = f"""
    SELECT
    s.station_name,
    {time_group_query}
    FROM waypoint w
    JOIN station s ON w.station_id = s.station_id
    {date_range_query}
    GROUP BY s.station_id, s.station_name
    ORDER BY total_delay_minutes DESC;
    """

    res = fetch_from_query("one", query)
    if res:
        return f"{res["station_name"]}, with a sum total of {res["total_delay_minutes"]} minutes"
    return "Unable to retrieve this information at this time."


def get_trains_cancelled_per_station_percentage(date_range: str, time_group: str):  # pylint: disable=unused-argument
    """get the trains cancelled per stations as a percentage"""
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
    s.station_name,
    c.cancelled_count,
    t.total_count,
    CASE
        WHEN t.total_count = 0 THEN 0
        ELSE ROUND((c.cancelled_count * 100.0 / t.total_count), 2)
    END AS cancel_percent
    FROM total_trains t
    JOIN cancelled_trains c ON t.station_id = c.station_id
    JOIN station s ON t.station_id = s.station_id;
    """
    res = fetch_from_query("all", query)
    return res


def get_avg_delays_all(date_range, time_group):  # pylint: disable=unused-argument
    """get the average delay for every station"""
    query = """
    SELECT
    s.station_name,
    ROUND(AVG(EXTRACT(EPOCH FROM (w.actual_arrival - w.booked_arrival)) / 60), 2) AS avg_arrival_delay,
    ROUND(AVG(EXTRACT(EPOCH FROM (w.actual_departure - w.booked_departure)) / 60), 2) AS avg_departure_delay
    FROM waypoint w
    JOIN station s ON s.station_id=w.station_id
    GROUP BY s.station_id
    """

    res = fetch_from_query("all", query)
    return res


def get_avg_delays_over_a_minute(date_range: str):
    """get the average delay over a minute for every station"""
    date_range_query = get_date_range_query(date_range, is_join=False)
    query = f"""
    SELECT
    s.station_name,
    ROUND(AVG( EXTRACT(EPOCH FROM (w.actual_arrival - w.booked_arrival)) / 60), 2)
    AS avg_arrival_delay,
    ROUND(AVG( EXTRACT(EPOCH FROM (w.actual_departure - w.booked_departure)) / 60), 2)
    AS avg_departure_delay
    FROM waypoint w
    JOIN station s ON s.station_id=w.station_id
    {date_range_query}
    AND EXTRACT(EPOCH FROM (w.actual_arrival - w.booked_arrival)) / 60 > 1
    GROUP BY s.station_name;
    """
    res = fetch_from_query("all", query)
    return res


def get_rolling_avg():
    """get the rolling average delay for every station"""
    query = """
    SELECT
    w.run_date,
    ROUND((AVG(EXTRACT(EPOCH FROM(w.actual_arrival - w.booked_arrival))) /60), 2)
    AS average_delay
    FROM waypoint w
    GROUP BY w.run_date
    """

    res = fetch_from_query("all", query)
    return res


def get_avg_delay():
    """get the average delay for every station"""
    query = """
    SELECT
        s.station_name,
        ROUND(AVG(CASE WHEN run_date = CURRENT_DATE - INTERVAL '1 day' THEN
                    EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) / 60 +
                    EXTRACT(EPOCH FROM (actual_departure - booked_departure)) / 60
                ELSE NULL
                END), 2) AS avg_delay_yday,
        ROUND(AVG(CASE WHEN run_date = CURRENT_DATE - INTERVAL '2 day' THEN
                    EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) / 60 +
                    EXTRACT(EPOCH FROM (actual_departure - booked_departure)) / 60
                ELSE NULL
                END), 2) AS avg_delay_day_before
    FROM waypoint w
    JOIN station s ON w.station_id = s.station_id
    WHERE run_date IN (CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE - INTERVAL '2 day')
    GROUP BY s.station_name, s.station_crs;
    """

    res = fetch_from_query("all", query)
    return res

# ---------- OPERATOR FUNCTIONS ----------


def get_cancellations_per_operator():
    """get the total cancellations for every operator"""
    query = """
    SELECT op.operator_id, op.operator_name, COUNT(c.cancellation_id) AS number_of_cancellations
    FROM operator op
    JOIN service s USING (operator_id) 
    JOIN waypoint w USING (service_id)
    JOIN cancellation c USING (waypoint_id)
    WHERE w.run_date >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY op.operator_id, op.operator_name
    """

    res = fetch_from_query("all", query)
    return res


def get_delay_count_over_5_minutes_per_operator():
    """get the total delays over five minutes for every operator"""
    query = """
    SELECT
    op.operator_name,
    COUNT(w.waypoint_id) AS number_of_delayed_trains
    FROM operator op
    LEFT JOIN service s USING (operator_id)
    LEFT JOIN waypoint w USING (service_id)
    WHERE (
    EXTRACT(EPOCH FROM (w.actual_arrival - w.booked_arrival)) / 60 > 5
    OR EXTRACT(EPOCH FROM (w.actual_departure - w.booked_departure)) / 60 > 5
    )
    GROUP BY op.operator_id, op.operator_name
    ORDER BY number_of_delayed_trains DESC
    """

    return fetch_from_query("all", query)


def get_proportion_of_large_delays_per_operator():
    """get the proportion of delays over 5 minutes for every operator"""
    query = """
    WITH delay_counts AS (
    SELECT
        op.operator_id,
        op.operator_name,
        COUNT(w.waypoint_id) AS total_trains,
        COUNT(CASE WHEN (
                EXTRACT(EPOCH FROM (w.actual_arrival - w.booked_arrival)) / 60 > 5
                OR EXTRACT(EPOCH FROM (w.actual_departure - w.booked_departure)) / 60 > 5
            ) THEN w.waypoint_id
            ELSE NULL
        END) AS total_delayed_trains
    FROM operator op
    LEFT JOIN service s USING (operator_id)
    LEFT JOIN waypoint w USING (service_id)
    LEFT JOIN cancellation c USING (waypoint_id)
    GROUP BY op.operator_id, op.operator_name
    )
    SELECT operator_id, operator_name, total_trains, total_delayed_trains,
        CASE WHEN total_trains > 0 
            THEN ROUND((total_delayed_trains * 100.0 / total_trains), 2) 
            ELSE 0
        END AS percent_delayed
    FROM delay_counts
    WHERE total_delayed_trains > 0
    ORDER BY percent_delayed DESC
    """

    return fetch_from_query("all", query)


def get_rolling_cancellation_per_operator():
    """get the total of cancellations for a rolling total of every operator"""
    query = """
    WITH delay_counts AS (
    SELECT
        w.run_date,
        COUNT(w.waypoint_id) AS total_trains,
        COUNT(CASE WHEN (
                EXTRACT(EPOCH FROM (w.actual_arrival - w.booked_arrival)) / 60 > 5
                OR EXTRACT(EPOCH FROM (w.actual_departure - w.booked_departure)) / 60 > 5
            ) THEN w.waypoint_id
            ELSE NULL
        END) AS total_delayed_trains
    FROM operator op
    LEFT JOIN service s USING (operator_id)
    LEFT JOIN waypoint w USING (service_id)
    LEFT JOIN cancellation c USING (waypoint_id)
    GROUP BY w.run_date
    )
    SELECT run_date, total_delayed_trains
    FROM delay_counts
    WHERE run_date IS NOT NULL
    """

    return fetch_from_query("all", query)


def get_greatest_delay(date_range, time_group):  # pylint: disable=unused-argument
    """get the greatest delay experienced for a waypoint"""
    time_group = "departure" if time_group == "sum total" else "arrival"
    query = f"""
    SELECT
    station_name,
    ROUND((EXTRACT(EPOCH FROM (w.actual_{time_group} - w.booked_{time_group})) / 60), 2) as delay,
    run_date
    FROM waypoint w
    JOIN station s USING (station_id)
    WHERE (EXTRACT(EPOCH FROM (w.actual_{time_group} - w.booked_{time_group})) / 60) IS NOT NULL
    ORDER BY (EXTRACT(EPOCH FROM (w.actual_{time_group} - w.booked_{time_group})) / 60) DESC
    """

    res = fetch_from_query("one", query)
    if res:
        return f"{res["station_name"]} had the highest delay at {res["delay"]} minutes"
    return "Unable to retrieve this information at this time"
