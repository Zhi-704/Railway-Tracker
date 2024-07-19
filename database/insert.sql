
INSERT INTO incident (incident_number, creation_time, incident_start, incident_end, is_planned, incident_summary, incident_description, incident_uri, affected_routes)
VALUES
('INC-001', 
'2024-07-01 08:30:00', 
'2024-07-01 08:00:00', 
'2024-05-01 10:00:00', 
False, 'Traffic Accident on Route 5', 
'A major accident involving multiple vehicles on Route 5 caused significant delays and road closures.', 
'http://example.com/incidents/001', 
'Route 5, Route 10'),
('INC-002', 
'2024-07-02 09:00:00',
 '2024-07-02 07:30:00', 
 '2024-06-18 12:00:00', 
 True, 
 'Scheduled Roadwork on Route 3', 
 'Planned roadwork for maintenance on Route 3. Expect lane closures and minor delays.', 
 'http://example.com/incidents/002', 
 'Route 3'),
('INC-003',
 '2024-07-03 15:45:00',
  '2024-07-03 14:30:00', 
  '2024-04-03 16:30:00', False,
   'Power Outage Affecting Route 8', 
   'An unexpected power outage disrupted traffic signals on Route 8, causing temporary traffic issues.', 
   'http://example.com/incidents/003', 
   'Route 8, Route 12');

SELECT incident_id FROM incident 
WHERE incident_end < TIMEZONE('Europe/London', CURRENT_TIMESTAMP);

INSERT into affected_operator (incident_id,operator_id )
VALUES (1, 1), (2, 2);

SELECT * FROM affected_operator;