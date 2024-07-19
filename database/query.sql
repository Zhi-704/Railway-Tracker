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



---- archive test:


-- SELECT * FROM station;
-- --  1 | BTH         | Bath Spa Rail Station

-- SELECT * FROM service;
-- -- 1 |          31 | C30127



-- INSERT INTO waypoint (
--     run_date, 
--     booked_arrival, 
--     actual_arrival, 
--     booked_departure, 
--     actual_departure, 
--     service_id, 
--     station_id
-- ) VALUES (
--     '2023-05-01', -- over a month ago
--     '2023-05-01 08:00:00', -- booked arrival time
--     '2023-05-01 08:50:00', -- actual arrival time
--     '2023-05-01 09:30:00', -- booked departure time
--     '2023-05-01 09:50:00', -- actual departure time
--     1, -- assuming service_id 1 exists in the service table
--     1  -- assuming station_id 1 exists in the station table
-- );

-- INSERT INTO waypoint (
--     run_date, 
--     booked_arrival, 
--     actual_arrival, 
--     booked_departure, 
--     actual_departure, 
--     service_id, 
--     station_id
-- ) VALUES (
--     '2023-04-01', -- over a month ago
--     '2023-05-01 08:00:00', -- booked arrival time
--     '2023-05-01 09:00:00', -- actual arrival time
--     '2023-05-01 09:10:00', -- booked departure time
--     '2023-05-01 09:50:00', -- actual departure time
--     1, -- assuming service_id 1 exists in the service table
--     1  -- assuming station_id 1 exists in the station table
-- );

-- INSERT INTO waypoint (
--     run_date, 
--     booked_arrival, 
--     actual_arrival, 
--     booked_departure, 
--     service_id, 
--     station_id
-- ) VALUES (
--     '2023-04-01', -- over a month ago
--     '2023-05-01 09:45:00', -- booked arrival time
--     '2023-05-01 09:00:00', -- actual arrival time
--     '2023-05-01 09:10:00', -- booked departure time, -- actual departure time
--     1, -- assuming service_id 1 exists in the service table
--     1  -- assuming station_id 1 exists in the station table
-- );

-- INSERT INTO cancellation(
--     cancel_code_id,
--     waypoint_id
-- ) VALUES (
--     1, 
--     3871
-- );
-- -- 99

-- SELECT * FROM cancellation
-- WHERE waypoint_id >= 3871;

-- SELECT *
-- FROM waypoint
-- WHERE run_date <= CURRENT_DATE - INTERVAL '1 month' ;
-- -- AND station_id = 1;
-- -- -- 3868
-- -- -- 3869
-- -- -- 3870

-- -- -- DELETE FROM waypoint
-- -- -- WHERE waypoint_id = 3859;

-- -- -- DELETE FROM waypoint
-- -- -- WHERE waypoint_id = 3860;

-- -- -- DELETE FROM cancellation
-- -- -- WHERE cancellation_id = 100

-- SELECT * FROM performance_archive;



-- SELECT * FROM operator;
--  1 | VT            | Avanti West Coast

-- SELECT incident_id, creation_time, incident_start, incident_end  FROM incident
-- WHERE incident_end < TIMEZONE('Europe/London', CURRENT_TIMESTAMP);



-- INSERT INTO incident (
--     incident_number,
--     creation_time,
--     incident_start,
--     incident_end,
--     is_planned,
--     incident_summary,
--     incident_description,
--     incident_uri,
--     affected_routes
-- ) VALUES (
--     'INC12345666666',
--     '2024-04-18 14:30:00',
--     '2024-10-10 10:00:00',
--     '2024-10-10 12:00:00',
--     True,
--     'System upgrade',
--     'Scheduled upgrade of the network infrastructure.',
--     'http://example.com/incident/INC1234576666',
--     'Route f, Route 5'
-- );
-- SELECT incident_id, creation_time, incident_start, incident_end  FROM incident
-- WHERE incident_end = '2024-10-10 12:00:00';

-- INSERT INTO affected_operator (
--     incident_id, operator_id
-- )VALUES (
--     '4 ',
--     '1'
-- );

-- INSERT INTO affected_operator (
--     incident_id, operator_id
-- )VALUES (
--     '2',
--     '1'
-- );

-- SELECT * FROM affected_operator;
-- 1, 2


-- SELECT constraint_name
-- FROM information_schema.table_constraints
-- WHERE table_name = 'affected_operator'
-- AND constraint_type = 'FOREIGN KEY';


