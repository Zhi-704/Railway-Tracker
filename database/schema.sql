-- Creates the schema for the database

DROP TABLE IF EXISTS incident, cancellation, station_performance_archive, users, cancel_code, station, subscription, waypoint, operator;

CREATE TABLE operator(
    operator_code CHAR(2) PRIMARY KEY,
    operator_name TEXT NOT NULL UNIQUE
);

CREATE TABLE station(
    station_crs CHAR(3) PRIMARY KEY,
    station_name TEXT NOT NULL UNIQUE
);

CREATE TABLE users(
    user_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE cancel_code(
    cancel_code CHAR(2) PRIMARY KEY,
    cause TEXT NOT NULL UNIQUE
);

CREATE TABLE incident(
    incident_number SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    operator_code CHAR(2) NOT NULL REFERENCES operator(operator_code),
    creation_time TIMESTAMP(0) NOT NULL,
    incident_start TIMESTAMP(0) NOT NULL,
    incident_end TIMESTAMP(0) NOT NULL,
    is_planned BOOLEAN NOT NULL,
    incident_summary TEXT NOT NULL,
    incident_description TEXT NOT NULL,
    incident_uri TEXT NOT NULL,
    affected_routes TEXT NOT NULL
);

CREATE TABLE station_performance_archive(
    performance_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    station_crs CHAR(3) NOT NULL REFERENCES station(station_crs),
    avg_delay SMALLINT NOT NULL,
    cancellation_count SMALLINT NOT NULL,
    creation_date TIMESTAMP(0) NOT NULL
);

CREATE TABLE subscription(
    subscription_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id SMALLINT NOT NULL REFERENCES users(user_id),
    operator_code CHAR(2) NOT NULL REFERENCES operator(operator_code)
);

CREATE TABLE waypoint(
    waypoint_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    run_date TIMESTAMP(0) NOT NULL,
    booked_arrival TIMESTAMP(0) NOT NULL,
    actual_arrival TIMESTAMP(0) NOT NULL,
    booked_departure TIMESTAMP(0) NOT NULL,
    actual_departure TIMESTAMP(0) NOT NULL,
    operator_code CHAR(2) NOT NULL REFERENCES operator(operator_code),
    station_crs CHAR(3) NOT NULL REFERENCES station(station_crs)
);

CREATE TABLE cancellation(
    cancellation_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    cancel_code CHAR(2) NOT NULL REFERENCES cancel_code(cancel_code),
    waypoint_id INT NOT NULL REFERENCES waypoint(waypoint_id)
);

CREATE TABLE affected_operator(
    affected_operator_id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    incident_number SMALLINT NOT NULL REFERENCES incident(incident_number),
    operator_code CHAR(2) NOT NULL REFERENCES operator(operator_code)
);