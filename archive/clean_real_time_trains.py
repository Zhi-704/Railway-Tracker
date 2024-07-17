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

    try:
        cur = db_connection.get_cursor(conn)
        cur.execute(query)

        conn.commit()
        station_ids = cur.fetchall()
        cur.close()

    except Exception as e:
        conn.rollback()

    return station_ids


def get_month_old_waypoints(conn: connection, station_id: str) -> list[dict]:
    """ Retrieves all waypoints that have a run_date of a month ago or more. """

    query = """
        SELECT *
        FROM waypoint
        WHERE run_date <= CURRENT_DATE - INTERVAL '1 month' 
            AND station_id = %s;
    """

    try:
        cur = db_connection.get_cursor(conn)
        cur.execute(query, (station_id,))

        conn.commit()
        waypoints = cur.fetchall()
        cur.close()

    except Exception as e:
        conn.rollback()

    return waypoints


def compute_avg_delay_for_station(conn: connection, station_id: int) -> dict:
    """ Computes and returns the average delay for a station, for trains that have 
        arrived/ departed over a month ago. """

    query = """
        SELECT 
            station_id,
            AVG(actual_arrival - booked_arrival) AS arrival_avg,
            AVG(actual_departure - booked_departure) AS departure_avg,
            AVG((actual_arrival - booked_arrival)+(actual_departure - booked_departure))avg_overall_delay
        FROM waypoint
        WHERE station_id = %s
            AND run_date <= CURRENT_DATE - INTERVAL '1 month'
        GROUP BY station_id;
    """

    try:
        cur = db_connection.get_cursor(conn)
        cur.execute(query, (station_id,))

        conn.commit()
        avg_delay = cur.fetchone()
        cur.close()

    except Exception as e:
        conn.rollback()

    return avg_delay

    # and later delete these waypoints - cascade?


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
    try:
        cur = db_connection.get_cursor(conn)
        cur.execute(query, (station_id,))

        conn.commit()
        cancellation_count = cur.fetchone()
        cur.close()

    except Exception as e:
        conn.rollback()

    return cancellation_count


def insert_performance_archive(conn: connection, archive_data: dict) -> None:
    """ Insert performance data about each station into the archive.
        Creation date is date of inserting into archive. """

    # can maybe do execute many, and pass in a list of dicts

    query = """
        INSERT INTO performance_archive (station_id, avg_delay, cancellation_count, creation_date) 
        VALUES (%s, %s, %s, TIMEZONE('Europe/London', CURRENT_TIMESTAMP));
    """

    try:
        cur = db_connection.get_cursor(conn)

        cur.execute(query, (
            archive_data["station_id"],
            archive_data["avg_delay"],
            archive_data["cancellation_count"],
        ))

        conn.commit()
        cur.close()
        logging.info("Clean: Inserted archive for station: %s",
                     archive_data["station_id"])

    except Exception as e:
        conn.rollback()
        logging.error("Load: Error occurred inserting incident %s", e)


def delete_cancellation(conn: connection, waypoint_id: int) -> None:
    """ Deletes a cancellation record by its waypoint id. """

    query = """
        DELETE FROM cancellation 
        WHERE waypoint_id = %s;
    """


def delete_waypoint(conn: connection, waypoint_id: int) -> None:
    """ Deletes a waypoint record by its waypoint id. """

    query = """
        DELETE FROM waypoint 
        WHERE waypoint_id = %s;
    """


def clean_real_time_trains_data():
    """ Cleans RealTimeTrains waypoints data from RDS based on how long ago the train journey
        occurred. Computed Performance statistics for the archiving process."""

    conn = db_connection.get_connection()

    # for each station:
    all_station_ids = get_all_stations(conn)

    for station in all_station_ids:
        station_id = station['station_id']

        # get old waypoints for this station:
        old_waypoints = get_month_old_waypoints(conn, station_id)

        # # 2) compute performance metrics
        avg_delay = compute_avg_delay_for_station(conn, station_id)
        if avg_delay:
            avg_delay = avg_delay['avg_overall_delay']

        cancellation_count = compute_cancellation_count_for_station(
            conn, station_id)
        if cancellation_count:
            cancellation_count = cancellation_count['cancellation_count']

        # print(station_id)
        # print(old_waypoints)
        # print(avg_delay)
        # print(cancellation_count)

        print("\n")

        # # 3) insert performance archive:
        data = {
            'station_id': station_id,
            'avg_delay': avg_delay,
            'cancellation_count': cancellation_count
        }

        # insert_performance_archive(conn, data)

        # # 4) deal with cancellations and services that they are connected to - delete from DB
        for waypoint in old_waypoints:

            delete_cancellation(conn, waypoint['waypoint_id'])
            delete_waypoint(conn, waypoint['waypoint_id'])

    conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    clean_real_time_trains_data()
