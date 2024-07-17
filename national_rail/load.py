""" Loads incident data into the RDS database. """
from os import environ
from dotenv import load_dotenv

from psycopg2 import connect
from psycopg2.extensions import connection, cursor
from psycopg2.extras import RealDictCursor, execute_values

import transform  # just for development


def get_connection() -> connection:
    """ Retrieves connection and returns it. """
    load_dotenv()
    return connect(
        user=environ['DB_USERNAME'],
        password=environ['DB_PASSWORD'],
        host=environ['DB_IP'],
        port=environ['DB_PORT'],
        dbname=environ['DB_NAME']
    )


def get_cursor(conn: connection) -> cursor:
    """ Retrieves cursor and returns it. """
    return conn.cursor(cursor_factory=RealDictCursor)


def upload_incident(conn: connection, incident: dict) -> int:
    """ Takes an incident and uploads to the database, returning the incident id. """

    query = """
        INSERT INTO incident (incident_number, creation_time, incident_start, incident_end, is_planned, incident_summary,
            incident_description, incident_uri, affected_routes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
        RETURNING incident_id;
    """

    cur = get_cursor(conn)
    cur.execute(query, (
        incident["incident_number"],
        incident["creation_time"],
        incident["start_time"],
        incident["end_time"],
        incident["is_planned"],
        incident["summary"],
        incident["description"],
        incident["uri"],
        incident["routes_affected"],

    ))

    incident_id = cur.fetchall()[0]['incident_id']
    conn.commit()
    cur.close()

    return incident_id


def check_if_exists(conn: connection, table_name: str, conditions: dict) -> bool:
    """ Checks if a certain data value already exists inside a relation. """

    query = f'''SELECT * FROM {table_name} WHERE {
        ' AND '.join([f'{key} = %s' for key in conditions.keys()])}'''

    cur = get_cursor(conn)
    cur.execute(query, tuple(conditions.values()))
    result = cur.fetchone()

    return result


def get_operator_code_id(conn: connection, operator_code: str) -> int | None:
    """ Retrieves operator id from operator table in database, by operator code. """

    operator = check_if_exists(conn, 'operator',
                               conditions={'operator_code': operator_code})
    if operator:
        return operator['operator_id']

    return None


def upload_affected_operator_assignment(conn: connection, incident_id: int, operator_id: str) -> None:
    """ Inserts an affected operator with an incident id and operator id. """

    query = """
        INSERT INTO affected_operator (incident_id, operator_id)
        VALUES (%s, %s)
        RETURNING affected_operator_id;
    """

    cur = get_cursor(conn)
    cur.execute(query, (incident_id, operator_id))

    conn.commit()
    cur.close()


def load_incidents(incidents_data: list[dict]) -> None:
    """ Loads all incidents created within the last 5 minutes to the RDS. """

    conn = get_connection()

    for incident in incidents_data:
        print(incident['incident_number'])

        incident_id = upload_incident(conn, incident)

        for operator_code in incident["operator_codes"]:
            operator_id = get_operator_code_id(conn, operator_code)

            if operator_id:
                upload_affected_operator_assignment(
                    conn, incident_id, operator_id)

    conn.close()


if __name__ == "__main__":
    load_incidents(transform.transform_national_rail_data("test_data.xml"))
    # just for development
