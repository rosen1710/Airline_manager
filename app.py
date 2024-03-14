from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
# from psycopg2 import sql
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Connect to the PostgreSQL database
def create_connection():
    conn = psycopg2.connect(
        dbname = 'airline_db',
        user = 'rosen',
        password = 'airline_manager',
        host = 'localhost',
        port = '6543'
    )
    return conn

# Create tables if they don't exist
def create_tables():
    try:
        conn = create_connection()
        cur = conn.cursor()

        destinations_table = """
            CREATE TABLE IF NOT EXISTS destinations (
                id SERIAL PRIMARY KEY,
                airport_name TEXT NOT NULL UNIQUE,
                airport_code TEXT NOT NULL UNIQUE,
                city TEXT NOT NULL,
                country TEXT NOT NULL,
                country_code TEXT NOT NULL
            );
        """

        aircrafts_table = """
            CREATE TABLE IF NOT EXISTS aircrafts (
                id SERIAL PRIMARY KEY,
                manufacturer TEXT NOT NULL,
                type TEXT NOT NULL,
                registration TEXT NOT NULL UNIQUE,
                km_range INTEGER NOT NULL,
                first_class_capacity INTEGER NOT NULL,
                economy_class_capacity INTEGER NOT NULL,
                location INTEGER REFERENCES destinations(id)
            );
        """

        flights_table = """
            CREATE TABLE IF NOT EXISTS flights (
                id SERIAL PRIMARY KEY,
                aircraft_id INTEGER REFERENCES aircrafts(id),
                flight_number TEXT NOT NULL,
                origin INTEGER REFERENCES destinations(id),
                destination INTEGER REFERENCES destinations(id),
                departure_time TIMESTAMP NOT NULL,
                arrival_time TIMESTAMP NOT NULL,
                first_class_ticket_price DECIMAL NOT NULL,
                economy_class_ticket_price DECIMAL NOT NULL
            );
        """

        cur.execute(destinations_table)
        cur.execute(aircrafts_table)
        cur.execute(flights_table)

        conn.commit()
        conn.close()
        print('Tables created or already exist')
    except:
        print('Error occurred while creating or accessing tables')
        exit()

# API endpoint to add a destination
@app.route('/destinations', methods=['POST'])
def add_destination():
    conn = create_connection()
    cur = conn.cursor()

    data = request.json
    airport_name = data['airport_name']
    airport_code = data['airport_code']
    city = data['city']
    country = data['country']
    country_code = data['country_code']

    try:
        cur.execute("INSERT INTO destinations (airport_name, airport_code, city, country, country_code) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                    (airport_name, airport_code, city, country, country_code))
    except psycopg2.errors.UniqueViolation:
        conn.commit()
        conn.close()
        return jsonify({"message": "This destination already exists"}), 400
    except:
        conn.commit()
        conn.close()
        return jsonify({"message": "An error occurred while adding destination"}), 500

    destination_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return jsonify({"message": "Destination added successfully", "destination_id": destination_id}), 201

# API endpoint to add an aircraft
@app.route('/aircrafts', methods=['POST'])
def add_aircraft():
    conn = create_connection()
    cur = conn.cursor()

    data = request.json
    manufacturer = data['manufacturer']
    type = data['type']
    registration = data['registration']
    km_range = data['km_range']
    first_class_capacity = data['first_class_capacity']
    economy_class_capacity = data['economy_class_capacity']
    location = data['location']

    try:
        cur.execute("INSERT INTO aircrafts (manufacturer, type, registration, km_range, first_class_capacity, economy_class_capacity, location) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;",
                    (manufacturer, type, registration, km_range, first_class_capacity, economy_class_capacity, location))
    except psycopg2.errors.UniqueViolation:
        conn.commit()
        conn.close()
        return jsonify({"message": "This aircraft already exists"}), 400
    except:
        conn.commit()
        conn.close()
        return jsonify({"message": "An error occurred while adding aircraft"}), 500

    aircraft_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return jsonify({"message": "Aircraft added successfully", "aircraft_id": aircraft_id}), 201

# API endpoint to add a flight
@app.route('/flights', methods=['POST'])
def add_flight():
    conn = create_connection()
    cur = conn.cursor()

    data = request.json
    aircraft_id = data['aircraft_id']
    flight_number = data['flight_number']
    origin = data['origin']
    destination = data['destination']
    departure_time = data['departure_time']
    arrival_time = data['arrival_time']
    first_class_ticket_price = data['first_class_ticket_price']
    economy_class_ticket_price = data['economy_class_ticket_price']

    # Check if the selected aircraft has any scheduled flights
    cur.execute("""
        SELECT arrival_time, destination
        FROM flights
        WHERE aircraft_id = %s
        ORDER BY arrival_time DESC
        LIMIT 1;
        """,
        (aircraft_id,))
    
    last_flight = cur.fetchone()

    if last_flight:
        last_arrival_time = last_flight[0]
        last_location = last_flight[1]

        # Check if the last location is the same as the new origin airport
        if last_location != origin:
            conn.close()
            return jsonify({"message": "Last location airport is not the same as the new origin airport"}), 400

        # Check if there is enough time between landing and the next takeoff
        if datetime.strptime(departure_time, "%Y-%m-%d %H:%M:%S.%f") < last_arrival_time + timedelta(hours=1.5):
            conn.close()
            return jsonify({"message": "Not enough time between landing and the next takeoff"}), 400
    
    else:
        cur.execute("""
            SELECT location
            FROM aircrafts
            WHERE id = %s;
            """,
            (aircraft_id,))
        
        last_location = cur.fetchone()

        # Check if the last location is the same as the new origin airport
        if last_location != origin:
            conn.close()
            return jsonify({"message": "Last location airport is not the same as the new origin airport"}), 400

    # Insert the flight into the database
    try:
        cur.execute("INSERT INTO flights (aircraft_id, flight_number, origin, destination, departure_time, arrival_time, first_class_ticket_price, economy_class_ticket_price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;",
            (aircraft_id, flight_number, origin, destination, departure_time, arrival_time, first_class_ticket_price, economy_class_ticket_price))
    except psycopg2.errors.UniqueViolation:
        conn.commit()
        conn.close()
        return jsonify({"message": "This flight already exists"}), 400
    except:
        conn.commit()
        conn.close()
        return jsonify({"message": "An error occurred while adding flight"}), 500

    flight_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return jsonify({"message": "Flight added successfully", "flight_id": flight_id}), 201

# Function to fetch all destinations
@app.route('/destinations', methods=['GET'])
def get_destinations():
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM destinations")
    destinations = cur.fetchall()

    conn.close()

    return jsonify({"destinations": destinations}), 200

# Function to fetch all aircrafts
@app.route('/aircrafts', methods=['GET'])
def get_aircrafts():
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM aircrafts")
    aircrafts = cur.fetchall()

    conn.close()

    return jsonify({"aircrafts": aircrafts}), 200

# Function to fetch all flights
@app.route('/flights', methods=['GET'])
def get_flights():
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM flights")
    flights = cur.fetchall()

    conn.close()

    return jsonify({"flights": flights}), 200

# Function to fetch flight's estimated earnings
@app.route('/flights/get-estimated-earnings/<int:flight_id>', methods=['GET'])
def get_flight_estimated_earnings(flight_id):
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT /* a.first_class_capacity * f.first_class_ticket_price AS first_class_earnings,
        a.economy_class_capacity * f.economy_class_ticket_price AS economy_class_earnings, */
        a.first_class_capacity * f.first_class_ticket_price + a.economy_class_capacity * f.economy_class_ticket_price AS total_earnings
        FROM flights f
        JOIN aircrafts a ON f.aircraft_id = a.id
        WHERE f.id = %s;
        """,
        (flight_id,))
    estimates = cur.fetchone()

    conn.close()

    return jsonify({"estimates": estimates}), 200

# Function to update a destination
@app.route('/destinations/<int:destination_id>', methods=['PUT'])
def update_destination(destination_id):
    conn = create_connection()
    cur = conn.cursor()

    data = request.json

    try:
        cur.execute("""
            UPDATE destinations 
            SET airport_name = %s, airport_code = %s, city = %s, country = %s, country_code = %s
            WHERE id = %s
            RETURNING id;
            """,
            (data['airport_name'], data['airport_code'], data['city'], data['country'], data['country_code'], destination_id))
    except:
        conn.commit()
        conn.close()
        return jsonify({"message": "An error occurred while updating destination"}), 500

    updated_destination_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return jsonify({"message": "Destination updated successfully", "destination_id": updated_destination_id}), 200

# Function to update an aircraft
@app.route('/aircrafts/<int:aircraft_id>', methods=['PUT'])
def update_aircraft(aircraft_id):
    conn = create_connection()
    cur = conn.cursor()

    data = request.json

    try:
        cur.execute("""
            UPDATE aircrafts 
            SET manufacturer = %s, type = %s, registration = %s, km_range = %s, first_class_capacity = %s, economy_class_capacity = %s, location = %s
            WHERE id = %s
            RETURNING id;
            """,
            (data['manufacturer'], data['type'], data['registration'], data['km_range'], data['first_class_capacity'], data['economy_class_capacity'], data['location'], aircraft_id))
    except:
        conn.commit()
        conn.close()
        return jsonify({"message": "An error occurred while updating aircraft"}), 500

    updated_aircraft_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return jsonify({"message": "Aircraft updated successfully", "aircraft_id": updated_aircraft_id}), 200

# Function to update a flight
@app.route('/flights/<int:flight_id>', methods=['PUT'])
def update_flight(flight_id):
    conn = create_connection()
    cur = conn.cursor()

    data = request.json

    try:
        cur.execute("""
            UPDATE flights 
            SET aircraft_id = %s, flight_number = %s, origin = %s, destination = %s, departure_time = %s, arrival_time = %s, first_class_ticket_price = %s, economy_class_ticket_price = %s
            WHERE id = %s
            RETURNING id;
            """,
            (data['aircraft_id'], data['flight_number'], data['origin'], data['destination'], data['departure_time'], data['arrival_time'], data['first_class_ticket_price'], data['economy_class_ticket_price'], flight_id))
    except:
        conn.commit()
        conn.close()
        return jsonify({"message": "An error occurred while updating flight"}), 500

    updated_flight_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return jsonify({"message": "Flight updated successfully", "flight_id": updated_flight_id}), 200

# Function to delete a destination
@app.route('/destinations/<int:destination_id>', methods=['DELETE'])
def delete_destination(destination_id):
    conn = create_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM destinations WHERE id = %s;", (destination_id,))
    except:
        conn.commit()
        conn.close()
        return jsonify({"message": "An error occurred while deleting destination"}), 500

    conn.commit()
    conn.close()

    return jsonify({"message": "Destination deleted successfully", "destination_id": destination_id}), 200

# Function to delete an aircraft
@app.route('/aircrafts/<int:aircraft_id>', methods=['DELETE'])
def delete_aircraft(aircraft_id):
    conn = create_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM aircrafts WHERE id = %s;", (aircraft_id,))
    except:
        conn.commit()
        conn.close()
        return jsonify({"message": "An error occurred while deleting aircraft"}), 500

    conn.commit()
    conn.close()

    return jsonify({"message": "Aircraft deleted successfully", "aircraft_id": aircraft_id}), 200

# Function to delete a flight
@app.route('/flights/<int:flight_id>', methods=['DELETE'])
def delete_flight(flight_id):
    conn = create_connection()
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM flights WHERE id = %s;", (flight_id,))
    except:
        conn.commit()
        conn.close()
        return jsonify({"message": "An error occurred while deleting flight"}), 500

    conn.commit()
    conn.close()

    return jsonify({"message": "Flight deleted successfully", "flight_id": flight_id}), 200

# Run create_tables function when the app starts
create_tables()

if __name__ == '__main__':
    app.run() # debug=True is possible, by default debug=False