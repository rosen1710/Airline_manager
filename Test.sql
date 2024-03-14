-- DROP TABLE flights;
-- DROP TABLE aircrafts;
-- DROP TABLE destinations;
-- INSERT INTO destinations VALUES (DEFAULT, 'Sofia International Airport', 'SOF', 'Sofia', 'Bulgaria', 'BG');
-- INSERT INTO destinations VALUES (DEFAULT, 'Varna Airport', 'VAR', 'Varna', 'Bulgaria', 'BG');
-- INSERT INTO destinations VALUES (DEFAULT, 'London Heathrow Airport', 'LHR', 'London', 'United Kingdom', 'UK');
-- INSERT INTO aircrafts VALUES (DEFAULT, 'Airbus', 'A320', 'LZ-FBD', 20000, 20, 200, 1);
-- INSERT INTO aircrafts VALUES (DEFAULT, 'Airbus', 'A319', 'LZ-PAR', 18000, 12, 160, 1);
-- INSERT INTO aircrafts VALUES (DEFAULT, 'Boeing', 'B738', 'LZ-ROM', 16000, 12, 180, 1);
-- INSERT INTO aircrafts VALUES (DEFAULT, 'Embraer', 'E190', 'LZ-VAR', 14000, 8, 92, 1);
-- INSERT INTO flights VALUES (DEFAULT, 1, 'FB977', 1, 2, NOW(), NOW(), 500, 140);
SELECT * FROM destinations;
SELECT * FROM aircrafts;
SELECT * FROM flights;
SELECT a.type AS aircraft, od.airport_code AS origin_airport, ad.airport_code AS destination_airport,
a.first_class_capacity * f.first_class_ticket_price AS first_class_earnings,
a.economy_class_capacity * f.economy_class_ticket_price AS economy_class_earnings,
a.first_class_capacity * f.first_class_ticket_price + a.economy_class_capacity * f.economy_class_ticket_price AS total_earnings
FROM flights f
JOIN aircrafts a ON f.aircraft_id = a.id
JOIN destinations od ON f.origin = od.id
JOIN destinations ad ON f.destination = ad.id;