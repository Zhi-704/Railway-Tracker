-- A file to query the database

-- SELECT incident_number, operator_code, creation_time FROM incident;
-- SELECT * FROM cancellation;
-- SELECT * FROM station_performance_archive;
-- SELECT * FROM users;
-- SELECT * FROM cancel_code;
-- SELECT * FROM station;
-- SELECT * FROM subscription;
-- SELECT * FROM waypoint;
-- SELECT * FROM operator;


SELECT incident_number, creation_time FROM incident;
SELECT * FROM affected_operator;


DELETE FROM affected_operator;
DELETE FROM incident;
