"""Create PDF with train summary details"""

import logging

from psycopg2.extensions import connection

from extract_pdf import get_connection, query_db


def get_cancelled_percentage(conn: connection) -> list[tuple]:
    """Calculates the percentage of cancelled trains for each station"""
    data = query_db(conn,
                    """WITH total_trains AS (
                        SELECT station_id, COUNT(*) AS total_count
                        FROM waypoint
                        GROUP BY station_id
                    ),
                    cancelled_trains AS (
                        SELECT station_id, COUNT(*) AS cancelled_count
                        FROM waypoint
                        JOIN cancellation USING (waypoint_id)
                        GROUP BY station_id
                    )
                    SELECT station_id, station_crs, station_name, cancelled_count, total_count,
                        CASE
                            WHEN total_count = 0 THEN 0
                            ELSE ROUND((cancelled_count * 100.0 / total_count), 2)
                        END AS cancellation_percentage
                    FROM total_trains
                    JOIN cancelled_trains USING (station_id)
                    JOIN station USING (station_id)""")
    logging.info("percentage of cancelled trains for each station: %s", data)
    return data


def get_delayed_percentage(conn: connection) -> list[tuple]:
    """Calculates the percentage of trains delayed more than 5 mins for each station"""
    data = query_db(conn,
                    """SELECT station_id,
                    ROUND(AVG(EXTRACT(EPOCH FROM(actual_arrival - booked_arrival)) / 60), 2) AS avg_arrival_delay_minutes,
                    ROUND(AVG(EXTRACT(EPOCH FROM(actual_departure - booked_departure)) / 60), 2) AS avg_departure_delay_minutes
                    FROM waypoint
                    GROUP BY station_id""")
    logging.info(
        "percentage of trains delayed more than 5 mins for each station: %s", data)
    return data


def get_avg_delay(conn: connection) -> list[tuple]:
    """Calculates the average delay for each station"""
    data = query_db(conn,
                    """SELECT station_id,
                        ROUND(AVG(
                            EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) / 60 +
                            EXTRACT(EPOCH FROM (actual_departure - booked_departure)) / 60
                        ), 2) AS avg_overall_delay_minutes
                    FROM waypoint
                    GROUP BY station_id;""")
    logging.info("average delay for each station: %s", data)
    return data


def get_avg_delay_long(conn: connection) -> list[tuple]:
    """Calculates the average delay more than 1 min for each station"""
    data = query_db(conn,
                    """SELECT station_id,
                        ROUND(AVG( EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) / 60), 2) 
                        AS avg_overall_delay_minutes
                    FROM waypoint
                    WHERE EXTRACT(EPOCH FROM (actual_arrival - booked_arrival)) / 60 > 1
                    GROUP BY station_id;""")
    logging.info("average delay more than 1 min for each station: %s", data)
    return data


def transform_pdf() -> None:
    conn = get_connection()
    get_cancelled_percentage(conn)
    get_delayed_percentage(conn)
    get_avg_delay(conn)
    get_avg_delay_long(conn)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    transform_pdf()
