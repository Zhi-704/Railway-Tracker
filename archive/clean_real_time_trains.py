""" This module works with old RealTimeTrains waypoint data from the RDS and 
    archives train data that is no longer needed. The archive contains the 
    performance metrics of the train data."""

import logging

from psycopg2.extensions import connection
import db_connection


def get_all_stations(conn: connection) -> list[dict]:
    """ Retrieves all waypoints that have a run_date of a month ago or more. """

    query = """
        SELECT station_id
        FROM station;
    """

    station_ids = db_connection.execute(conn, query, ())

    return station_ids


def get_month_old_waypoints(conn: connection, station_id: str) -> list[dict]:
    """ Retrieves all waypoints that have a run_date of a month ago or more. """

    query = """
        SELECT *
        FROM waypoint
        WHERE run_date <= CURRENT_DATE - INTERVAL '1 month' 
            AND station_id = %s;
    """

    outdated_waypoints = db_connection.execute(conn, query, (station_id,))

    return outdated_waypoints


def compute_avg_delay_for_station(conn: connection, station_id: int) -> dict:
    """ Computes and returns the average delay for a station, for trains that have 
        arrived/ departed over a month ago. """

    query = """
        SELECT 
            station_id,
            AVG((actual_arrival - booked_arrival)+(actual_departure - booked_departure))avg_overall_delay
        FROM waypoint
        WHERE station_id = %s
            AND run_date <= CURRENT_DATE - INTERVAL '1 month'
        GROUP BY station_id;
    """

    avg_delay = db_connection.execute(conn, query, (station_id,))

    if avg_delay:
        avg_delay = avg_delay[0]['avg_overall_delay']
    return avg_delay


def compute_cancellation_count_for_station(conn: connection, station_id: int) -> dict:
    """ Computes and returns the number of cancellations for a station, for trains that 
        have arrived/ departed over a month ago. """

    query = """
        SELECT 
            COUNT(cancellation_id) AS cancellation_count
        FROM waypoint w
        JOIN cancellation c 
        ON c.waypoint_id = w.waypoint_id
        WHERE w.station_id = %s
            AND run_date <= CURRENT_DATE - INTERVAL '1 month';
    """

    cancellation_count = db_connection.execute(conn, query, (station_id,))

    if cancellation_count:
        cancellation_count = cancellation_count[0]['cancellation_count']

    return cancellation_count


def insert_performance_archive(conn: connection, archive_data: dict) -> None:
    """ Insert performance data about each station into the archive.
        Creation date is date of inserting into archive. """

    query = """
        INSERT INTO performance_archive (station_id, avg_delay, cancellation_count, creation_date) 
        VALUES (%s, %s, %s, TIMEZONE('Europe/London', CURRENT_TIMESTAMP));
    """

    db_connection.execute_without_result(conn, query, (archive_data["station_id"],
                                                       archive_data["avg_delay"],
                                                       archive_data["cancellation_count"],))


def delete_cancellation(conn: connection, waypoint_id: int) -> None:
    """ Deletes a cancellation record by its waypoint id. """

    query = """
        DELETE FROM cancellation 
        WHERE waypoint_id = %s;
    """
    db_connection.execute_without_result(conn, query, (waypoint_id,))


def delete_waypoint(conn: connection, waypoint_id: int) -> None:
    """ Deletes a waypoint record by its waypoint id. """

    query = """
        DELETE FROM waypoint 
        WHERE waypoint_id = %s;
    """
    db_connection.execute_without_result(conn, query, (waypoint_id,))


def get_table_size(conn: connection, table_name: str) -> int:
    """ Returns the size of the table given by the table_name argument. """

    query = f"""
        SELECT COUNT(*) FROM {table_name};
    """
    return db_connection.execute(conn, query, ())


def clean_real_time_trains_data():
    """ Cleans RealTimeTrains waypoints data from RDS based on how long ago the train journey
        occurred. Computes performance statistics for the archiving process and inserts
        into archive.  """

    conn = db_connection.get_connection()

    all_station_ids = get_all_stations(conn)

    for station in all_station_ids:
        station_id = station['station_id']

        old_waypoints = get_month_old_waypoints(conn, station_id)
        if old_waypoints:

            avg_delay = compute_avg_delay_for_station(conn, station_id)
            cancellation_count = compute_cancellation_count_for_station(
                conn, station_id)

            data = {
                'station_id': station_id,
                'avg_delay': avg_delay.total_seconds() / 60,
                'cancellation_count': cancellation_count
            }
            insert_performance_archive(conn, data)

            for waypoint in old_waypoints:
                delete_cancellation(conn, waypoint['waypoint_id'])
                delete_waypoint(conn, waypoint['waypoint_id'])

            logging.info(
                "Outdated data archived for station: %s", station_id)
        else:
            logging.info(
                "No outdated data found for station: %s", station_id)

    conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    clean_real_time_trains_data()
