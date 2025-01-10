import os
import sys
import sqlite3
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app import init_db  # Upewnij sie, ze DB_PATH jest poprawnie importowane

DB_PATH = "/home/raspi/Desktop/ProjektZaliczeniowy/Projekt/tests/test_database.db"

class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(DB_PATH):
            print(f"Baza danych {DB_PATH} nie istnieje. Tworzenie nowej...")
            init_db(DB_PATH)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()

        required_tables = ['weather_control', 'air_control', 'water_control']
        for table in required_tables:
            self.assertIn((table,), tables, f"Brak tabeli: {table}")
        print("Poprawna inicjalizacja bazy danych oraz tabel.")

    def test_weather_control_insert_and_read(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO weather_control 
                       (temperature, humidity) 
                       VALUES (?, ?)""", (22.5, 45.0))
        conn.commit()

        cursor.execute("""SELECT * FROM weather_control 
                       WHERE temperature = 22.5 AND humidity = 45.0""")
        result = cursor.fetchone()
        conn.close()

        if result:
            print("""Test weather_control_insert_and_read: 
                  Wstawianie i odczyt danych powiodly sie.\n""")
        else:
            print("""Test weather_control_insert_and_read: 
                  Nie udalo sie odczytac danych.\n""")

        self.assertIsNotNone(result, "Nie udalo sie odczytac danych z tabeli weather_control\n")
        self.assertEqual(result[2], 22.5)
        self.assertEqual(result[3], 45.0)

    def test_air_control_insert_and_read(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO air_control 
                       (pm25, pm10, temperature, humidity, air_quality) 
                       VALUES (?, ?, ?, ?, ?)""",
                       (12.5, 20.0, 22.5, 45.0, "Good"))
        conn.commit()

        cursor.execute("SELECT * FROM air_control WHERE pm25 = 12.5 AND pm10 = 20.0")
        result = cursor.fetchone()
        conn.close()

        if result:
            print("""Test air_control_insert_and_read: 
                  Wstawianie i odczyt danych powiodly sie.\n""")
        else:
            print("""Test air_control_insert_and_read: 
                  Nie udalo sie odczytac danych.\n""")

        self.assertIsNotNone(result, "Nie udalo sie odczytac danych z tabeli air_control\n")
        self.assertEqual(result[2], 12.5)
        self.assertEqual(result[3], 20.0)

    def test_water_control_insert_and_read(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO water_control 
                       (ph, adjustment, current_ph, temperature) 
                       VALUES (?, ?, ?, ?)""",
                       (7.5, "Increase", 7.8, 22.5))
        conn.commit()

        cursor.execute("""SELECT * FROM water_control 
                       WHERE ph = 7.5 AND adjustment = 'Increase'""")
        result = cursor.fetchone()
        conn.close()

        if result:
            print("""Test water_control_insert_and_read: 
                  Wstawianie i odczyt danych powiodly sie.\n""")
        else:
            print("""Test water_control_insert_and_read: 
                  Nie udalo sie odczytac danych.\n""")

        self.assertIsNotNone(result, "Nie udalo sie odczytac danych z tabeli water_control\n")
        self.assertEqual(result[2], 7.5)
        self.assertEqual(result[3], "Increase")

    def test_weather_control_update(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO weather_control 
                       (temperature, humidity) 
                       VALUES (?, ?)""", (22.5, 45.0))
        conn.commit()

        cursor.execute("""UPDATE weather_control 
                       SET temperature = 25.0 WHERE humidity = 45.0""")
        conn.commit()

        cursor.execute("""SELECT temperature 
                       FROM weather_control WHERE humidity = 45.0""")
        result = cursor.fetchone()
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
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO air_control 
                       (pm25, pm10, temperature, humidity, air_quality) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (12.5, 20.0, 22.5, 45.0, "Good"))
        conn.commit()

        cursor.execute("""DELETE FROM air_control 
                       WHERE pm25 = 12.5 AND pm10 = 20.0""")
        conn.commit()

        cursor.execute("SELECT * FROM air_control WHERE pm25 = 12.5 AND pm10 = 20.0")
        result = cursor.fetchone()
        conn.close()

        if not result:
            print("Test air_control_delete: Usuniecie danych powiodlo sie.\n")
        else:
            print("Test air_control_delete: Nie udalo sie usunac danych.\n")

        self.assertIsNone(result, "Nie udalo sie usunac danych z tabeli air_control\n")

if __name__ == '__main__':
    
    full_db_path = os.path.abspath(DB_PATH)
    print(f"\n\nFull DB_PATH for testing: {full_db_path}\n\n")
    unittest.main()
