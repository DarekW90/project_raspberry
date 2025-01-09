import os
import sys
import sqlite3
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app import init_db  # Upewnij sie, ze DB_PATH jest poprawnie importowane

DB_PATH = "/home/raspi/Desktop/ProjektZaliczeniowy/Projekt/tests/test_database.db"

class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        # Wywołanie funkcji inicjalizującej bazę danych
        if not os.path.exists(DB_PATH):
            print(f"Baza danych {DB_PATH} nie istnieje. Tworzenie nowej...")
            init_db(DB_PATH)  # Tworzenie bazy danych i tabel, jesli jeszcze nie istnieja
        
        # Sprawdzanie, czy tabele istnieją
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        # Wypisz wszystkie tabele w bazie danych
        print(f"Tabele w bazie danych: {tables}")
        
        # Upewnij się, że odpowiednie tabele istnieją
        required_tables = ['weather_control', 'air_control', 'water_control']
        for table in required_tables:
            self.assertIn((table,), tables, f"Brak tabeli: {table}")

    def test_weather_control_insert_and_read(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Test wstawiania i odczytu danych z tabeli weather_control
        cursor.execute("INSERT INTO weather_control (temperature, humidity) VALUES (?, ?)", (22.5, 45.0))
        conn.commit()

        cursor.execute("SELECT * FROM weather_control WHERE temperature = 22.5 AND humidity = 45.0")
        result = cursor.fetchone()
        conn.close()

        # Sprawdzenie, czy dane zostały zapisane poprawnie
        self.assertIsNotNone(result, "Nie udało się odczytać danych z tabeli weather_control")
        self.assertEqual(result[2], 22.5)
        self.assertEqual(result[3], 45.0)

    def test_air_control_insert_and_read(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Test wstawiania i odczytu danych z tabeli air_control
        cursor.execute("INSERT INTO air_control (pm25, pm10, temperature, humidity, air_quality) VALUES (?, ?, ?, ?, ?)",
                       (12.5, 20.0, 22.5, 45.0, "Good"))
        conn.commit()

        cursor.execute("SELECT * FROM air_control WHERE pm25 = 12.5 AND pm10 = 20.0")
        result = cursor.fetchone()
        conn.close()

        # Sprawdzenie, czy dane zostały zapisane poprawnie
        self.assertIsNotNone(result, "Nie udało się odczytać danych z tabeli air_control")
        self.assertEqual(result[2], 12.5)
        self.assertEqual(result[3], 20.0)

    def test_water_control_insert_and_read(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Test wstawiania i odczytu danych z tabeli water_control
        cursor.execute("INSERT INTO water_control (ph, adjustment, current_ph, temperature) VALUES (?, ?, ?, ?)",
                       (7.5, "Increase", 7.8, 22.5))
        conn.commit()

        cursor.execute("SELECT * FROM water_control WHERE ph = 7.5 AND adjustment = 'Increase'")
        result = cursor.fetchone()
        conn.close()

        # Sprawdzenie, czy dane zostały zapisane poprawnie
        self.assertIsNotNone(result, "Nie udało się odczytać danych z tabeli water_control")
        self.assertEqual(result[2], 7.5)
        self.assertEqual(result[3], "Increase")


if __name__ == '__main__':
    
    full_db_path = os.path.abspath(DB_PATH)
    print(f"\n\nFull DB_PATH for testing: {full_db_path}\n\n")
    unittest.main()
