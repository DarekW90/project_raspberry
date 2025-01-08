import sqlite3

# ?cie?ka do bazy danych
DB_PATH = "measurements.db"

# Funkcja dodaj?ca nowe kolumny
def add_column_to_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Dodajemy kolumn? `ph` (REAL) do tabeli `measurements`
        cursor.execute("ALTER TABLE measurements ADD COLUMN pm25 REAL")
        cursor.execute("ALTER TABLE measurements ADD COLUMN pm10 REAL")
        cursor.execute("ALTER TABLE measurements ADD COLUMN air_quality TEXT")
        print("Kolumny zostaly pomyslnie dodane.")
    except sqlite3.OperationalError as e:
        print(f"B??d: {e}")
    finally:
        conn.commit()
        conn.close()

# Uruchomienie funkcji
add_column_to_table()