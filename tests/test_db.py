"""This file contains unit tests for the database functions. 
It tests the insertion and retrieval of data in the 
weather_control, air_control, and water_control tables. 
It also tests the update of data in the weather_control table 
and the deletion of data from the air_control table."""
import os
import sys
import sqlite3
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))


from app import init_db  # Upewnij sie, ze DB_PATH jest poprawnie importowane

DB_PATH="/home/raspi/Desktop/ProjektZaliczeniowy/Projekt/tests/test_database.db"

class TestDatabaseFunctions(unittest.TestCase):
    """
    Klasa zawierająca testy jednostkowe dla funkcji bazy danych.
    Metody testowe:
    - test_weather_control_insert_and_read:
    Testuje wstawianie i odczytywanie danych w tabeli weather_control.
    - test_air_control_insert_and_read:
    Testuje wstawianie i odczytywanie danych w tabeli air_control.
    - test_water_control_insert_and_read:
    Testuje wstawianie i odczytywanie danych w tabeli water_control.
    - test_weather_control_update:
    Testuje aktualizację danych w tabeli weather_control.
    - test_air_control_delete:
    Testuje usuwanie danych z tabeli air_control.
    """

    def setUp(self):
        """
        Metoda ustawiająca środowisko testowe.
        Sprawdza czy baza danych istnieje, jeśli nie, tworzy nową.
        Następnie nawiązuje połączenie z bazą danych i pobiera listę tabel.
        Sprawdza czy wymagane tabele istnieją w bazie danych.
        Jeśli tabela nie istnieje, zgłasza błąd.
        """
        # kod metody setUp

        if not os.path.exists(DB_PATH):
            print(f"Baza danych {DB_PATH} nie istnieje. Tworzenie nowej...")
            init_db(DB_PATH)

        conn=sqlite3.connect(DB_PATH)
        cursor=conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables=cursor.fetchall()
        conn.close()

        required_tables=['weather_control', 'air_control', 'water_control']
        for table in required_tables:
            self.assertIn((table,), tables, f"Brak tabeli: {table}")
        print("Poprawna inicjalizacja bazy danych oraz tabel.")

    def test_weather_control_insert_and_read(self):
        """
        Testuje wstawianie i odczytywanie danych z tabeli weather_control.
        Sprawdza czy dane zostają poprawnie wstawione do tabeli weather_control
        oraz czy można je później odczytać.
        W przypadku powodzenia testu, wypisuje komunikat
        "Wstawianie i odczyt danych powiodły się".
        W przypadku niepowodzenia testu, wypisuje komunikat
        "Nie udało się odczytać danych".
        Sprawdza również czy dane zostały odczytane poprawnie z tabeli weather_control.
        Jeśli dane nie zostały odczytane, wypisuje komunikat
        "Nie udało się odczytać danych z tabeli weather_control".
        Sprawdza czy wartość temperatury w odczytanych danych jest równa 22.5.
        Sprawdza czy wartość wilgotności w odczytanych danych jest równa 45.0.
        """

        conn=sqlite3.connect(DB_PATH)
        cursor=conn.cursor()

        cursor.execute("""INSERT INTO weather_control
                       (temperature, humidity)
                       VALUES (?, ?)""", (22.5, 45.0))
        conn.commit()

        cursor.execute("""SELECT * FROM weather_control
                       WHERE temperature=22.5 AND humidity=45.0""")
        result=cursor.fetchone()
        conn.close()

        if result:
            print("""Test weather_control_insert_and_read:
                  Wstawianie i odczyt danych powiodly sie.\n""")
        else:
            print("""Test weather_control_insert_and_read:
                  Nie udalo sie odczytac danych.\n""")

        self.assertIsNotNone(result,
                             "Nie udalo sie odczytac danych z tabeli weather_control\n")
        self.assertEqual(result[2], 22.5)
        self.assertEqual(result[3], 45.0)

    def test_air_control_insert_and_read(self):
        """
        Testuje wstawianie i odczytywanie danych w tabeli air_control.
        Sprawdza czy dane zostają poprawnie wstawione do tabeli air_control,
        a następnie czy można je odczytać.
        Wartości wstawiane do tabeli:
        - pm25: 12.5
        - pm10: 20.0
        - temperature: 22.5
        - humidity: 45.0
        - air_quality: "Good"
        Po wstawieniu danych, sprawdzane jest czy dane
        zostały odczytane poprawnie. Jeśli tak, wypisuje komunikat
        "Wstawianie i odczyt danych powiodły się".
        W przeciwnym razie, wypisuje komunikat "Nie udało się odczytać danych".
        Sprawdza również czy wartości odczytane z tabeli są zgodne
        z oczekiwanymi wartościami:
        - result[2] powinno być równe 12.5
        - result[3] powinno być równe 20.0
        """

        conn=sqlite3.connect(DB_PATH)
        cursor=conn.cursor()

        cursor.execute("""INSERT INTO air_control
                       (pm25, pm10, temperature, humidity, air_quality) 
                       VALUES (?, ?, ?, ?, ?)""",
                       (12.5, 20.0, 22.5, 45.0, "Good"))
        conn.commit()

        cursor.execute("SELECT * FROM air_control WHERE pm25=12.5 AND pm10=20.0")
        result=cursor.fetchone()
        conn.close()

        if result:
            print("""Test air_control_insert_and_read:
                  Wstawianie i odczyt danych powiodly sie.\n""")
        else:
            print("""Test air_control_insert_and_read:
                  Nie udalo sie odczytac danych.\n""")

        self.assertIsNotNone(result,
                             "Nie udalo sie odczytac danych z tabeli air_control\n")
        self.assertEqual(result[2], 12.5)
        self.assertEqual(result[3], 20.0)

    def test_water_control_insert_and_read(self):
        """
        Testuje wstawianie i odczytywanie danych w tabeli water_control.
        Sprawdza czy dane zostają poprawnie wstawione do tabeli water_control
        oraz czy można je później odczytać.
        Wartości wstawiane do tabeli:
        - ph: 7.5
        - adjustment: "Increase"
        - current_ph: 7.8
        - temperature: 22.5
        Po wstawieniu danych, sprawdzane jest czy dane zostały odczytane poprawnie
        i czy wartości w kolumnach ph i adjustment są zgodne z oczekiwanymi.
        Jeśli dane zostaną poprawnie odczytane,
        wypisuje komunikat "Wstawianie i odczyt danych powiodły się".
        W przeciwnym razie, wypisuje komunikat
        "Nie udało się odczytać danych".
        Sprawdza również czy wynik odczytu nie
        jest pusty oraz czy wartości w kolumnach ph i adjustment
        są zgodne z oczekiwanymi.
        """

        conn=sqlite3.connect(DB_PATH)
        cursor=conn.cursor()

        cursor.execute("""INSERT INTO water_control
                       (ph, adjustment, current_ph, temperature)
                       VALUES (?, ?, ?, ?)""",
                       (7.5, "Increase", 7.8, 22.5))
        conn.commit()

        cursor.execute("""SELECT * FROM water_control
                       WHERE ph=7.5 AND adjustment='Increase'""")
        result=cursor.fetchone()
        conn.close()

        if result:
            print("""Test water_control_insert_and_read:
                  Wstawianie i odczyt danych powiodly sie.\n""")
        else:
            print("""Test water_control_insert_and_read:
                  Nie udalo sie odczytac danych.\n""")

        self.assertIsNotNone(result,
                             "Nie udalo sie odczytac danych z tabeli water_control\n")
        self.assertEqual(result[2], 7.5)
        self.assertEqual(result[3], "Increase")

    def test_weather_control_update(self):
        """
        Testuje aktualizację danych w tabeli weather_control.
        Sprawdza, czy aktualizacja danych temperatury w
        tabeli weather_control powiodła się.
        Metoda wykonuje następujące kroki:
        1. Nawiązuje połączenie z bazą danych.
        2. Wstawia dane do tabeli weather_control.
        3. Aktualizuje temperaturę na 25.0 dla wpisu o wilgotności 45.0.
        4. Pobiera temperaturę dla wpisu o wilgotności 45.0.
        5. Zamyka połączenie z bazą danych.
        6. Sprawdza, czy aktualizacja danych powiodła się.
        7. Sprawdza, czy pobrana temperatura wynosi 25.0.
        W przypadku powodzenia aktualizacji danych, wyświetla komunikat
        "Aktualizacja danych powiodła się".
        W przeciwnym razie, wyświetla komunikat "Nie udało się zaktualizować danych".
        Jeśli nie udało się zaktualizować danych w tabeli weather_control,
        wyświetla komunikat "Nie udało się zaktualizować danych w tabeli weather_control".
        """

        conn=sqlite3.connect(DB_PATH)
        cursor=conn.cursor()

        cursor.execute("""INSERT INTO weather_control
                       (temperature, humidity)
                       VALUES (?, ?)""", (22.5, 45.0))
        conn.commit()

        cursor.execute("""UPDATE weather_control
                       SET temperature=25.0 WHERE humidity=45.0""")
        conn.commit()

        cursor.execute("""SELECT temperature
                       FROM weather_control WHERE humidity=45.0""")
        result=cursor.fetchone()
        conn.close()

        if result and result[0] == 25.0:
            print("""Test weather_control_update:
                  Aktualizacja danych powiodla sie.\n""")
        else:
            print("""Test weather_control_update:
                  Nie udalo sie zaktualizowac danych.\n""")

        self.assertIsNotNone(result, """Nie udalo sie zaktualizowac danych w tabeli
                             weather_control\n""")
        self.assertEqual(result[0], 25.0)

    def test_air_control_delete(self):
        """
        Testuje funkcję usuwania danych z tabeli air_control.
        Sprawdza, czy dane zostają poprawnie usunięte z tabeli air_control.
        Tworzy połączenie z bazą danych, dodaje dane do tabeli,
        usuwa dane z tabeli,
        a następnie sprawdza, czy dane zostały usunięte poprzez
        wykonanie zapytania SELECT.
        Jeśli dane nie są już dostępne w tabeli, wypisuje komunikat
        "Test air_control_delete: Usuniecie danych powiodlo sie.",
        w przeciwnym razie wypisuje komunikat "Test air_control_delete:
        Nie udalo sie usunac danych.".
        Na końcu sprawdza, czy wynik zapytania SELECT jest równy None,
        jeśli tak, wypisuje komunikat
        "Nie udalo sie usunac danych z tabeli air_control".
        """

        conn=sqlite3.connect(DB_PATH)
        cursor=conn.cursor()

        cursor.execute("""INSERT INTO air_control
                       (pm25, pm10, temperature, humidity, air_quality)
                       VALUES (?, ?, ?, ?, ?)""",
                    (12.5, 20.0, 22.5, 45.0, "Good"))
        conn.commit()

        cursor.execute("""DELETE FROM air_control
                       WHERE pm25=12.5 AND pm10=20.0""")
        conn.commit()

        cursor.execute("SELECT * FROM air_control WHERE pm25=12.5 AND pm10=20.0")
        result=cursor.fetchone()
        conn.close()

        if not result:
            print("Test air_control_delete: Usuniecie danych powiodlo sie.\n")
        else:
            print("Test air_control_delete: Nie udalo sie usunac danych.\n")

        self.assertIsNone(result, "Nie udalo sie usunac danych z tabeli air_control\n")

if __name__ == '__main__':
    full_db_path=os.path.abspath(DB_PATH)
    print(f"\n\nFull DB_PATH for testing: {full_db_path}\n\n")
    unittest.main()
