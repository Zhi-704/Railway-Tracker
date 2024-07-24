-- A file to query the database
SELECT incident_number, creation_time FROM incident;
SELECT * FROM cancellation;
SELECT * FROM performance_archive;
SELECT * FROM subscriber;
SELECT * FROM cancel_code;
SELECT * FROM station;
SELECT * FROM waypoint;
SELECT * FROM operator;
SELECT * FROM affected_operator;
SELECT * FROM service;

SELECT COUNT(*) AS waypoint_count FROM waypoint;
--  17947
SELECT COUNT(*) AS archive_count FROM performance_archive;
-- 1