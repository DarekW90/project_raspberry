"""Klasa testowa dla testowania tras w aplikacji Flask."""

import unittest
import requests


class FlaskRoutesTestCase(unittest.TestCase):
    """Klasa testowa dla testowania tras w aplikacji Flask.
    Metody testowe:
    - test_check_server(): Sprawdza, czy serwer jest dostepny.
    - test_landing_page(): Testuje strone glowna aplikacji.
    - test_measurements_page(): Testuje strone z pomiarami.
    - test_aquarium_page(): Testuje strone z Akwarium.
    - test_air_quality_page(): Testuje strone dotyczaca jakosci powietrza.
    - test_camera_page(): Testuje strone z kamera.
    Wszystkie metody testowe wykonuja zapytania HTTP na odpowiednie adresy URL serwera
    i sprawdzaja status odpowiedzi. Jesli status jest inny niz 200, test konczy sie niepowodzeniem.
    W przypadku bledu polaczenia z serwerem, test rowniez konczy sie niepowodzeniem.
    - AssertionError: Jesli status odpowiedzi jest inny niz 200.
    - self.fail: Jesli nie mozna polaczyc sie z serwerem.
    :param unittest.TestCase: Klasa bazowa dla testow jednostkowych"""

    BASE_URL = "http://127.0.0.1:5000"

    def test_check_server(self):
        """
        Sprawdza, czy serwer jest dostepny.
        Metoda wykonuje zapytanie GET na podstawowy adres URL serwera.
        Jesli odpowiedz serwera ma kod innny niz 200, wypisuje
        komunikat "Server offline".
        W przeciwnym razie wypisuje komunikat "Server is running!".
        Jesli wystapi blad podczas wykonywania zapytania,
        metoda konczy sie niepowodzeniem
        i wypisuje komunikat z informacja o bledzie.
        :param self: Obiekt testowy
        :return: None
        """

        try:
            response = requests.get(self.BASE_URL)
            # print(f"Odpowiedz dla serwera : {response}")
            if response.status_code != 200:
                print("Server offline")
            else:
                print("Server is running!")
        except requests.exceptions.RequestException:
            self.fail("Failed to connect to the server")

    def test_landing_page(self):
        """
        Testuje strone glowna aplikacji.
        Sprawdza, czy mozna poprawnie nawiazac polaczenie
        z serwerem i czy otrzymano odpowiedz o kodzie 200.
        Jesli nie mozna nawiazac polaczenia,
        test konczy sie niepowodzeniem.
        Raises:
            AssertionError: Jesli nie otrzymano
            odpowiedzi o kodzie 200.
        """

        try:
            response = requests.get(f"{self.BASE_URL}/")
            # print(f"Odpowiedz dla landing page : {response}")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony glownej - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Landing Page")

    def test_measurements_page(self):
        """
        Testuje strone z pomiarami.
        Sprawdza, czy mozna poprawnie pobrac strone z pomiarami z serwera.
        Jesli polaczenie z serwerem nie powiedzie sie,
        test zostanie zakonczony niepowodzeniem.
        Raises:
            AssertionError: Jesli status odpowiedzi
            nie jest rowny 200.
        """

        try:
            response = requests.get(f"{self.BASE_URL}/measurements_page")
            # print(f"Odpowiedz dla measurement page : {response}")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony z pomiarami - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Measurements Page")

    def test_aquarium_page(self):
        """
        Testuje strone z Akwarium.
        Sprawdza, czy mozna poprawnie pobrac strone z Akwarium z serwera.
        Jesli polaczenie z serwerem jest udane i status odpowiedzi wynosi 200,
        wypisuje komunikat "Test response: dla strony z Akwarium - OK".
        Jesli wystapi blad polaczenia, test konczy sie niepowodzeniem
        i wypisuje komunikat "Nie mozna polaczyc sie z serwerem: Akwarium".
        """

        try:
            response = requests.get(f"{self.BASE_URL}/aquarium")
            # print(f"Odpowiedz dla aquarium page : {response}")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony z Akwarium - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Akwarium")

    def test_air_quality_page(self):
        """
        Testuje strone dotyczaca jakosci powietrza.
        Sprawdza, czy mozna pobrac odpowiedz z serwera
        dla strony o adresie {self.BASE_URL}/air_quality.
        Oczekiwany kod odpowiedzi to 200.
        Jesli nie mozna polaczyc sie z serwerem,
        test konczy sie niepowodzeniem.
        Raises:
            AssertionError: Jesli kod odpowiedzi jest inny niz 200.
            self.fail: Jesli nie mozna polaczyc sie z serwerem.
        """

        try:
            response = requests.get(f"{self.BASE_URL}/air_quality")
            # print(f"Odpowiedz dla air quality page : {response}")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony z Jakosci Powietrza - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Jakosci Powietrza")

    def test_camera_page(self):
        """
        Testuje strone z kamera.
        Sprawdza, czy mozna poprawnie polaczyc sie
        z serwerem i otrzymac odpowiedz o kodzie 200.
        Jesli nie mozna polaczyc sie z serwerem,
        test konczy sie niepowodzeniem.
        """

        try:
            response = requests.get(f"{self.BASE_URL}/door_bell_page")
            # print(f"Odpowiedz dla camera page : {response}")
            self.assertEqual(response.status_code, 200)
            print("Test response: dla strony z Kamera - OK")
        except requests.exceptions.ConnectionError:
            self.fail("Nie mozna polaczyc sie z serwerem: Kamera")


if __name__ == '__main__':
    unittest.main()
