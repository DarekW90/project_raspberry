import unittest
import requests


class FlaskRoutesTestCase(unittest.TestCase):
    
    BASE_URL = "http://127.0.0.1:5000"  # Zmień na odpowiedni adres serwera, jeśli potrzebne
    
    def test_check_server(self):
        try:
            response = requests.get(self.BASE_URL)
            if response.status_code != 200:
                print("Server offline")
            else:
                print("Server is running!")
        except requests.exceptions.RequestException:
            self.fail(f"Failed to connect to the server")

    def test_landing_page(self):
        try:
            response = requests.get(f"{self.BASE_URL}/")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony glownej - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Landing Page")

    def test_measurements_page(self):
        try:
            response = requests.get(f"{self.BASE_URL}/measurements_page")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony z pomiarami - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Measurements Page")

    def test_aquarium_page(self):
        try:
            response = requests.get(f"{self.BASE_URL}/aquarium")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony z Akwarium - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Akwarium")

    def test_air_quality_page(self):
        try:
            response = requests.get(f"{self.BASE_URL}/air_quality")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony z Jakosci Powietrza - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Jakości Powietrza")

    def test_camera_page(self):
        try:
            response = requests.get(f"{self.BASE_URL}/door_bell_page")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony z Kamera - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Kamera")


if __name__ == '__main__':
    unittest.main()
