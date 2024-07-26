-- A file to query the database
-- SELECT incident_number, creation_time FROM incident;
-- SELECT * FROM cancellation;
-- SELECT * FROM performance_archive;
-- SELECT * FROM subscriber;
-- SELECT * FROM cancel_code;
-- SELECT * FROM station;
-- SELECT * FROM waypoint;
-- SELECT * FROM operator;
-- SELECT * FROM affected_operator;
-- SELECT * FROM service;


SELECT COUNT(*) as waypoints_yester FROM waypoint
WHERE run_date = CURRENT_DATE - INTERVAL '1 day';
-- 3178

SELECT COUNT(*) as waypoints FROM waypoint;
SELECT COUNT(*) as cancellations FROM cancellation;

 
 --- deletes
-- DELETE FROM cancellation
-- WHERE waypoint_id IN (
--     SELECT waypoint_id
--     FROM waypoint
--     WHERE run_date = CURRENT_DATE - INTERVAL '1 day'
-- );

-- DELETE FROM waypoint
-- WHERE run_date = CURRENT_DATE - INTERVAL '1 day';



-- -- selects
-- SELECT COUNT(*) as waypoints FROM waypoint;
-- SELECT COUNT(*) as cancellations FROM cancellation;
-- SELECT COUNT(*) FROM waypoint
-- WHERE run_date = CURRENT_DATE - INTERVAL '1 day';


-- SELECT COUNT(*) FROM waypoint;