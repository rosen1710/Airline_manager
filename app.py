from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
# from psycopg2 import sql

app = Flask(__name__)
CORS(app)

# PostgreSQL database details
DB_NAME = 'airline_db'
DB_USER = 'rosen'
DB_PASSWORD = 'airline_manager'
DB_HOST = 'database' # 'localhost'
DB_PORT = '5432' # '6543'

# Connect to the PostgreSQL database
def create_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
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
                airport_name TEXT NOT NULL,
                city TEXT NOT NULL,
                country TEXT NOT NULL,
                country_code TEXT NOT NULL
            );
        """

        aircrafts_table = """
            CREATE TABLE IF NOT EXISTS aircrafts (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
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
    city = data['city']
    country = data['country']
    country_code = data['country_code']

    cur.execute("INSERT INTO destinations (airport_name, city, country, country_code) VALUES (%s, %s, %s, %s) RETURNING id;",
                (airport_name, city, country, country_code))
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
    name = data['name']
    km_range = data['km_range']
    first_class_capacity = data['first_class_capacity']
    economy_class_capacity = data['economy_class_capacity']
    location = data['location']

    cur.execute("INSERT INTO aircrafts (name, km_range, first_class_capacity, economy_class_capacity, location) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                (name, km_range, first_class_capacity, economy_class_capacity, location))
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

    cur.execute("INSERT INTO flights (aircraft_id, flight_number, origin, destination, departure_time, arrival_time, first_class_ticket_price, economy_class_ticket_price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;",
                (aircraft_id, flight_number, origin, destination, departure_time, arrival_time, first_class_ticket_price, economy_class_ticket_price))
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

    return jsonify({"destinations": destinations})

# Function to fetch all aircrafts
@app.route('/aircrafts', methods=['GET'])
def get_aircrafts():
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM aircrafts")
    aircrafts = cur.fetchall()

    conn.close()

    return jsonify({"aircrafts": aircrafts})

# Function to fetch all flights
@app.route('/flights', methods=['GET'])
def get_flights():
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM flights")
    flights = cur.fetchall()

    conn.close()

    return jsonify({"flights": flights})

# Function to update a destination
@app.route('/destinations/<int:destination_id>', methods=['PUT'])
def update_destination(destination_id):
    conn = create_connection()
    cur = conn.cursor()

    data = request.json
    # You can update specific columns here based on your requirements
    cur.execute("""
        UPDATE destinations 
        SET airport_name = %s, city = %s, country = %s, country_code = %s
        WHERE id = %s
        RETURNING id;
        """,
        (data['airport_name'], data['city'], data['country'], data['country_code'], destination_id))

    updated_destination_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return jsonify({"message": "Destination updated successfully", "destination_id": updated_destination_id})

# Function to delete a destination
@app.route('/destinations/<int:destination_id>', methods=['DELETE'])
def delete_destination(destination_id):
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM destinations WHERE id = %s;", (destination_id,))
    conn.commit()

    conn.close()

    return jsonify({"message": "Destination deleted successfully", "destination_id": destination_id})

# Function to update an aircraft
@app.route('/aircrafts/<int:aircraft_id>', methods=['PUT'])
def update_aircraft(aircraft_id):
    conn = create_connection()
    cur = conn.cursor()

    data = request.json
    # You can update specific columns here based on your requirements
    cur.execute("""
        UPDATE aircrafts 
        SET name = %s, km_range = %s, first_class_capacity = %s, economy_class_capacity = %s, location = %s
        WHERE id = %s
        RETURNING id;
        """,
        (data['name'], data['km_range'], data['first_class_capacity'], data['economy_class_capacity'], data['location'], aircraft_id))

    updated_aircraft_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return jsonify({"message": "Aircraft updated successfully", "aircraft_id": updated_aircraft_id})

# Function to delete an aircraft
@app.route('/aircrafts/<int:aircraft_id>', methods=['DELETE'])
def delete_aircraft(aircraft_id):
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM aircrafts WHERE id = %s;", (aircraft_id,))
    conn.commit()

    conn.close()

    return jsonify({"message": "Aircraft deleted successfully", "aircraft_id": aircraft_id})

# Function to update a flight
@app.route('/flights/<int:flight_id>', methods=['PUT'])
def update_flight(flight_id):
    conn = create_connection()
    cur = conn.cursor()

    data = request.json
    # You can update specific columns here based on your requirements
    cur.execute("""
        UPDATE flights 
        SET aircraft_id = %s, flight_number = %s, origin = %s, destination = %s, departure_time = %s, arrival_time = %s, first_class_ticket_price = %s, economy_class_ticket_price = %s
        WHERE id = %s
        RETURNING id;
        """,
        (data['aircraft_id'], data['flight_number'], data['origin'], data['destination'], data['departure_time'], data['arrival_time'], data['first_class_ticket_price'], data['economy_class_ticket_price'], flight_id))

    updated_flight_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return jsonify({"message": "Flight updated successfully", "flight_id": updated_flight_id})

# Function to delete a flight
@app.route('/flights/<int:flight_id>', methods=['DELETE'])
def delete_flight(flight_id):
    conn = create_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM flights WHERE id = %s;", (flight_id,))
    conn.commit()

    conn.close()

    return jsonify({"message": "Flight deleted successfully", "flight_id": flight_id})

# Run create_tables function when the app starts
create_tables()

if __name__ == '__main__':
    app.run(debug=True)