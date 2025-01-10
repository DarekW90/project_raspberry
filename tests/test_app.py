"""Klasa testowa dla testowania tras w aplikacji Flask."""

import unittest
import requests


class FlaskRoutesTestCase(unittest.TestCase):
    """Klasa testowa dla testowania tras w aplikacji Flask.
    Metody testowe:
    - test_check_server(): Sprawdza, czy serwer jest dostępny.
    - test_landing_page(): Testuje stronę główną aplikacji.
    - test_measurements_page(): Testuje stronę z pomiarami.
    - test_aquarium_page(): Testuje stronę z Akwarium.
    - test_air_quality_page(): Testuje stronę dotyczącą jakości powietrza.
    - test_camera_page(): Testuje stronę z kamerą.
    Wszystkie metody testowe wykonują zapytania HTTP na odpowiednie adresy URL serwera
    i sprawdzają status odpowiedzi. Jeśli status jest inny niż 200, test kończy się niepowodzeniem.
    W przypadku błędu połączenia z serwerem, test również kończy się niepowodzeniem.
    - AssertionError: Jeśli status odpowiedzi jest inny niż 200.
    - self.fail: Jeśli nie można połączyć się z serwerem.
    :param unittest.TestCase: Klasa bazowa dla testów jednostkowych"""

    BASE_URL = "http://127.0.0.1:5000"

    def test_check_server(self):
        """
        Sprawdza, czy serwer jest dostępny.
        Metoda wykonuje zapytanie GET na podstawowy adres URL serwera.
        Jeśli odpowiedź serwera ma kod innny niż 200, wypisuje
        komunikat "Server offline".
        W przeciwnym razie wypisuje komunikat "Server is running!".
        Jeśli wystąpi błąd podczas wykonywania zapytania,
        metoda kończy się niepowodzeniem
        i wypisuje komunikat z informacją o błędzie.
        :param self: Obiekt testowy
        :return: None
        """

        try:
            response = requests.get(self.BASE_URL)
            if response.status_code != 200:
                print("Server offline")
            else:
                print("Server is running!")
        except requests.exceptions.RequestException:
            self.fail("Failed to connect to the server")

    def test_landing_page(self):
        """
        Testuje stronę główną aplikacji.
        Sprawdza, czy można poprawnie nawiązać połączenie
        z serwerem i czy otrzymano odpowiedź o kodzie 200.
        Jeśli nie można nawiązać połączenia,
        test kończy się niepowodzeniem.
        Raises:
            AssertionError: Jeśli nie otrzymano
            odpowiedzi o kodzie 200.
        """

        try:
            response = requests.get(f"{self.BASE_URL}/")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony glownej - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Landing Page")

    def test_measurements_page(self):
        """
        Testuje stronę z pomiarami.
        Sprawdza, czy można poprawnie pobrać stronę z pomiarami z serwera.
        Jeśli połączenie z serwerem nie powiedzie się,
        test zostanie zakończony niepowodzeniem.
        Raises:
            AssertionError: Jeśli status odpowiedzi
            nie jest równy 200.
        """
        self.fail("Nie można połączyć się z serwerem: Measurements Page")

        try:
            response = requests.get(f"{self.BASE_URL}/measurements_page")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony z pomiarami - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Measurements Page")

    def test_aquarium_page(self):
        """
        Testuje stronę z Akwarium.
        Sprawdza, czy można poprawnie pobrać stronę z Akwarium z serwera.
        Jeśli połączenie z serwerem jest udane i status odpowiedzi wynosi 200,
        wypisuje komunikat "Test response: dla strony z Akwarium - OK".
        Jeśli wystąpi błąd połączenia, test kończy się niepowodzeniem
        i wypisuje komunikat "Nie można połączyć się z serwerem: Akwarium".
        """
        self.fail("Nie można połączyć się z serwerem: Akwarium")

        try:
            response = requests.get(f"{self.BASE_URL}/aquarium")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony z Akwarium - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Akwarium")

    def test_air_quality_page(self):
        """
        Testuje stronę dotyczącą jakości powietrza.
        Sprawdza, czy można pobrać odpowiedź z serwera
        dla strony o adresie {self.BASE_URL}/air_quality.
        Oczekiwany kod odpowiedzi to 200.
        Jeśli nie można połączyć się z serwerem,
        test kończy się niepowodzeniem.
        Raises:
            AssertionError: Jeśli kod odpowiedzi jest inny niż 200.
            self.fail: Jeśli nie można połączyć się z serwerem.
        """
        self.fail("Nie można połączyć się z serwerem: Jakości Powietrza")

        try:
            response = requests.get(f"{self.BASE_URL}/air_quality")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony z Jakosci Powietrza - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Jakości Powietrza")

    def test_camera_page(self):
        """
        Testuje stronę z kamerą.
        Sprawdza, czy można poprawnie połączyć się
        z serwerem i otrzymać odpowiedź o kodzie 200.
        Jeśli nie można połączyć się z serwerem,
        test kończy się niepowodzeniem.
        """
        self.fail("Nie można połączyć się z serwerem: Kamera")

        try:
            response = requests.get(f"{self.BASE_URL}/door_bell_page")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony z Kamera - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Kamera")


if __name__ == '__main__':
    unittest.main()
