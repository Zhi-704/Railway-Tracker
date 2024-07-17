-- A file to query the database

-- SELECT incident_number, creation_time FROM incident;
-- SELECT * FROM cancellation;
-- SELECT * FROM station_performance_archive;
-- SELECT * FROM users;
-- SELECT * FROM cancel_code;
-- SELECT * FROM operator;
-- SELECT * FROM station;
-- SELECT * FROM subscription;

-- -- SELECT * FROM waypoint;
-- -- SELECT * FROM operator;

-- INSERT INTO service (
--     operator_id,
--     service_uid
-- ) VALUES (
--     1, -- Avanti West Coast, VT 
--     'SVC123456'
-- );

-- SELECT * FROM service;

-- INSERT INTO waypoint (
--     run_date,
--     booked_arrival,
--     actual_arrival,
--     booked_departure,
--     actual_departure,
--     service_id,
--     station_id
-- ) VALUES (
--     '2024-05-17 08:30:00', -- run_date 2 months ago
--     '2023-05-15 09:00:00', 
--     '2023-05-15 09:30:00',
--     '2023-05-15 11:00:00',
--     '2023-05-15 11:25:00', 
--     11, -- service_id
--     1 -- station_id = Bath Spa Rail Station, BTH
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
--     '2024-05-17 08:30:00', -- run_date 2 months ago
--     '2023-05-15 09:00:00', 
--     '2023-05-15 10:10:00',
--     '2023-05-15 11:20:00',
--     '2023-05-15 12:25:00', 
--     11, -- service_id
--     1 -- station_id = Bath Spa Rail Station, BTH
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
--     '2024-07-17 08:30:00', -- run_date today
--     '2023-05-15 09:00:00', 
--     '2023-05-15 09:10:00',
--     '2023-05-15 09:20:00',
--     '2023-05-15 09:25:00', 
--     11, -- service_id
--     1 -- station_id = Bath Spa Rail Station, BTH
-- );


-- SELECT * FROM service;

SELECT * FROM waypoint;

-- DELETE FROM waypoint;
-- DELETE FROM service;


SELECT station_id,
AVG(EXTRACT(EPOCH FROM (actual_departure - booked_departure)) / 60) AS avg_delay_minutes
FROM waypoint
WHERE station_id = 1
    AND run_date <= CURRENT_DATE - INTERVAL '1 month' 
GROUP BY station_id;

SELECT station_id,
AVG(actual_departure - booked_departure) AS diff
FROM waypoint
WHERE station_id = 1
    AND run_date <= CURRENT_DATE - INTERVAL '1 month' 
GROUP BY station_id;

SELECT 
    station_id,
    AVG(actual_arrival - booked_arrival) AS arrival_avg,
    AVG(actual_departure - booked_departure) AS departure_avg,
    AVG((actual_arrival - booked_arrival)+(actual_departure - booked_departure))avg_overall_delay
FROM waypoint
WHERE station_id = 1
    AND run_date <= CURRENT_DATE - INTERVAL '1 month'
GROUP BY station_id;


