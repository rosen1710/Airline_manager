import unittest
import requests
from datetime import datetime, timedelta

class TestFlightsAPI(unittest.TestCase):
    def test_runner(self):
        test_add_destination()
        test_add_aircraft()
        test_add_flight()
        test_flight_earnings_estimate()

def test_add_destination():
    # Test the add_destination endpoint
    payload = {
        "airport_name": "Paris Charles de Gaulle Airport",
        "airport_code": "CDG",
        "city": "Paris",
        "country": "France",
        "country_code": "FR"
    }
    print(f"\n{requests.post("http://127.0.0.1:5000/destinations", json=payload).text}")

    response = requests.get("http://127.0.0.1:5000/destinations").json()
    for item in response:
        print(f"{item}: {response[item]}")

def test_add_aircraft():
    # Test the add_aircraft endpoint
    payload = {
        "manufacturer": "Bombardier",
        "type": "Global 8000",
        "registration": "LZ-SOF",
        "km_range": 14000,
        "first_class_capacity": 19,
        "economy_class_capacity": 0,
        "location": 1
    }
    print(f"\n{requests.post("http://127.0.0.1:5000/aircrafts", json=payload).text}")

    response = requests.get("http://127.0.0.1:5000/aircrafts").json()
    for item in response:
        print(f"{item}: {response[item]}")

def test_add_flight():
    # Test the add_flight endpoint
    payload = {
        "aircraft_id": 1,
        "flight_number": "FB978",
        "origin": 2,
        "destination": 1,
        "departure_time": str(datetime.now() + timedelta(hours=2)),
        "arrival_time": str(datetime.now() + timedelta(hours=2, minutes=45)),
        "first_class_ticket_price": 450,
        "economy_class_ticket_price": 150
    }
    print(f"\n{requests.post("http://127.0.0.1:5000/flights", json=payload).text}")

    response = requests.get("http://127.0.0.1:5000/flights").json()
    for item in response:
        print(f"{item}: {response[item]}")

def test_flight_earnings_estimate():
    print("")
    response = requests.get("http://127.0.0.1:5000/flights/get-estimated-earnings/1").json()
    for item in response:
        print(f"{item}: {response[item]}")

if __name__ == '__main__':
    unittest.main()