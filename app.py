from datetime import datetime
import sqlite3
import threading
import random
import os
import time
import cv2
from threading import Lock # Lock do synchronizacji dostepu do zasobow
from flask import Flask, jsonify, request, render_template, Response
from flask_socketio import SocketIO, emit

# Konfiguracja Flask i SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Global variable to store the last frame
camera_lock = Lock()
LAST_FRAME = None

# Konfiguracja bazy danych
# DB_NAME = "measurements.db"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "measurements.db")

def init_db(DB_PATH):
    """Inicjalizacja bazy danych."""

    print(f"DB_PATH: {os.path.abspath(DB_PATH)}")

    if not os.path.exists(DB_PATH):
        print("Baza danych nie istnieje. Tworze nowa...")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Tworzenie tabeli dla weather control
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_control (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                temperature REAL,
                humidity REAL
            )
        """)

        # Tworzenie tabeli dla air control
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS air_control (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                pm25 REAL,
                pm10 REAL,
                temperature REAL,
                humidity REAL,
                air_quality TEXT
            )
        """)

        # Tworzenie tabeli dla water control
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS water_control (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ph REAL,
                adjustment TEXT,
                current_ph REAL,
                temperature REAL
            )
        """)

        conn.commit()
        conn.close()
        print(f"Baza danych zostala zainicjalizowana. w folderze {DB_PATH}")  # Dodano ten komunikat
    except Exception as e:
        print(f"Wystapil blad podczas inicjalizacji bazy danych: {e}")


def capture_camera():
    """Obsluguje kamere, odczytujac klatki i zapisujac je do globalnej zmiennej."""
    global LAST_FRAME
    try:
        camera = cv2.VideoCapture(0)
        
        if not camera.isOpened():
            raise RuntimeError("Nie mozna uzyskac dostepu do kamery.")

        while True:
            success, frame = camera.read()
            if not success:
                break

            with camera_lock:
                LAST_FRAME = frame.copy()  # Aktualizuj globalna klatke

            # Dodaj opoznienie, aby uniknac przeciazenia CPU
            time.sleep(0.05)
    except RuntimeError:
        print("\n\n\033[91m" + 20 * "-" + " Nie wykryto kamery " + 20 * "-" + "\033[0m\n\n")
    finally:
        if "camera" in locals() and camera.isOpened():
            camera.release()


def generate_frames():
    """Generuje strumien wideo z najnowszych klatek."""
    global LAST_FRAME
    while True:
        with camera_lock:
            if LAST_FRAME is None:
                continue
            _, buffer = cv2.imencode('.jpg', LAST_FRAME)
            frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def detect_motion():
    """Wykrywa ruch na podstawie najnowszych klatek,
    zapisuje zdjecie i rysuje kwadrat wokol wykrytego ruchu."""
    global LAST_FRAME
    prev_frame_gray = None

    # Sciezka do folderu "phototrap"
    photo_dir = "phototrap"

    # Jezli "phototrap" nie jest katalogiem, utworz go
    if not os.path.isdir(photo_dir):
        print(f"Tworzenie katalogu {photo_dir}")
        os.makedirs(photo_dir)

    while True:
        with camera_lock:
            if LAST_FRAME is None:
                continue
            frame = LAST_FRAME.copy()

        # Przetwarzanie klatki
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

        if prev_frame_gray is None:
            prev_frame_gray = gray_frame
            continue

        # Analiza roznic miedzy klatkami
        frame_delta = cv2.absdiff(prev_frame_gray, gray_frame)
        _, thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Znajd? kontury
        contours, _ = cv2.findContours(thresh.copy(),
                                       cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        motion_detected = False

        for contour in contours:
            if cv2.contourArea(contour) > 25000:  # Jezli kontur jest wystarczajaco duzy
                motion_detected = True

                # Rysowanie prostokata wokol konturu
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if motion_detected:
            print("Ruch wykryty!")
            socketio.emit('motion', {'status': 'motion_detected'})

            # Zapisz zdjecie
            timestamp = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
            filename = f"picture_{timestamp}.jpg"

            filename = os.path.join(photo_dir, f"picture_{timestamp}.jpg")
            cv2.imwrite(filename, frame)

            print(f"Zdjecie zapisane jako {filename}")

            # Czekaj 10 sekund przed nastepnym zapisem
            time.sleep(10)

        prev_frame_gray = gray_frame
        time.sleep(0.1)  # Unikaj przeciazenia CPU



### ROUTES ###

@app.route('/')
def landing_page():
    """
    Renderuje stronę docelową, zwracając szablon index.html.
    Zwraca:
    Wyrenderowany szablon index.html.
    """

    return render_template('index.html')


@app.route('/measurements_page')
def measurements_page():
    """
    Pobiera najnowsze 10 pomiarów kontroli pogody z 
    bazy danych i renderuje je w szablonie measurements.html.
    Zwraca:
    Wyrenderowany szablon z danymi pomiarów.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM weather_control 
                   ORDER BY timestamp DESC LIMIT 10""")
    measurements = cursor.fetchall()
    conn.close()
    # Przekaz dane pomiarow do szablonu
    return render_template('measurements.html', measurements=measurements)


@app.route('/history_page')
def history_page():
    """
    Pobiera historyczne pomiary pogody z bazy danych i renderuje je w szablonie.
    Zwraca:
    Wyrenderowany szablon z historycznymi pomiarami pogody.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weather_control ORDER BY timestamp")
    measurements = cursor.fetchall()
    conn.close()
    # Przekaz dane pomiarow do szablonu
    return render_template('measurements.html', measurements=measurements)


# Endpointy REST API
@app.route('/measurements', methods=['GET'])
def get_measurements():
    """Zwraca ostatnie pomiary z bazy danych."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM measurements ORDER BY timestamp DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    measurements = [
        {"id": row[0], "timestamp": row[1], "temperature": row[2], "humidity": row[3]}
        for row in rows
    ]
    return jsonify(measurements)

@app.route('/history', methods=['GET'])
def get_history():
    """Zwraca wszystkie pomiary."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM measurements")
    rows = cursor.fetchall()
    conn.close()
    measurements = [
        {"id": row[0], "timestamp": row[1], "temperature": row[2], "humidity": row[3]}
        for row in rows
    ]
    return jsonify(measurements)


@app.route('/alert', methods=['POST'])
def set_alert():
    """Ustawienie progu alertu dla temperatury lub wilgotnosci."""
    data = request.json
    threshold_temp = data.get("temperature", None)
    threshold_hum = data.get("humidity", None)
    if threshold_temp is not None:
        print(f"Ustawiono prog alertu dla temperatury: {threshold_temp}C")
    if threshold_hum is not None:
        print(f"Ustawiono prog alertu dla wilgotnosci: {threshold_hum}%")
    return jsonify({"message": "Alert ustawiony!"}), 200


# Obsluga WebSocket
@socketio.on('connect')
def handle_connect():
    """
    Funkcja obsługująca połączenie klienta.
    Wypisuje informację o połączeniu klienta oraz 
    emituje wiadomość o statusie połączenia.
    Parametry:
        Brak
    Zwraca:
        Brak
    """

    print("Klient polaczony")
    emit('status', {'message': 'Polaczono z serwerem Raspberry Pi'})


@app.route('/door_bell_page')
def door_bell_page():
    """
    Funkcja zwracająca szablon strony 'camera.html'.
    :return: Szablon strony 'camera.html'.
    """
    
    return render_template('camera.html')


@app.route('/video_feed')
def video_feed():
    """
    Funkcja zwraca strumień wideo w formacie
    multipart/x-mixed-replace; boundary=frame.
    Wykorzystuje funkcję generate_frames() do
    generowania kolejnych klatek wideo.
    """

    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/aquarium')
def ph_measurements_page():
    """
    Funkcja zwraca stronę z pomiarami pH.
    :return: Szablon HTML strony z pomiarami pH.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT id, timestamp, temperature, ph, adjustment
                   FROM water_control
                   ORDER BY timestamp DESC LIMIT 20
                   """)
    measurements = cursor.fetchall()
    conn.close()
    return render_template('aquarium.html',measurements=measurements)

@app.route('/air_quality')
def air_quality_page():
    """
    Funkcja zwraca stronę z pomiarami jakości powietrza.
    :return: Szablon HTML strony z pomiarami jakości powietrza.
    :rtype: str
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT id, timestamp, temperature,
                   pm25, pm10, humidity, air_quality 
                   FROM air_control 
                   ORDER BY timestamp DESC LIMIT 20
                   """)
    measurements = cursor.fetchall()
    conn.close()
    return render_template('air_quality.html',
                           measurements=measurements)


### FUNKCJE SYMULUJACE ###

# Funkcja symulujaca dane z sensora
def simulate_sensor():
    """
    Symuluje odczyty z czujnika temperatury i wilgotności.
    Funkcja generuje losowe dane temperatury i wilgotności
    w określonym zakresie,
    zapisuje je do bazy danych oraz wysyła przez WebSocket.
    Returns:
        None
    """

    while True:
        # Generowanie losowych danych
        temperature = round(random.uniform(20.0, 30.0), 1)
        humidity = round(random.uniform(40.0, 60.0), 1)
        print(f"Symulacja: Temp={temperature}C, Wilgotnosc={humidity}%")
        
        # Zapis danych do bazy
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO weather_control
                       (temperature, humidity)
                       VALUES (?, ?)""",
                       (temperature, humidity))
        conn.commit()
        conn.close()

        # Wysylanie danych przez WebSocket
        socketio.emit('measurement', {'temperature': temperature, 'humidity': humidity})
        
        # Odczyt co 10 sekund
        time.sleep(10)


# Funkcja symulujaca kontrole pH wody
def simulate_ph_control():
    """
    Symuluje kontrolę pH w akwarium.
    Funkcja generuje losowe wartości pomiarowe dla
    pH i temperatury w zakresie określonym przez parametry.
    Następnie symuluje regulację pH w akwarium na podstawie
    docelowego pH i szybkości zmiany pH.
    Wyniki pomiarów i działania regulacji są wyświetlane
    na konsoli oraz zapisywane do bazy danych.
    Parametry:
    - target_ph (float): Docelowe pH wody (neutralne).
    - adjustment_rate (float): Szybkość zmiany pH w wyniku regulacji.
    Zwraca:
    - None
    Wymagane moduły:
    - random
    - sqlite3
    - time
    """

    target_ph = 7.0
    adjustment_rate = 0.1

    while True:
        # Generowanie losowych wartosci pomiarowych
        current_ph = round(random.uniform(6.0, 8.0), 2)
        temperature = round(random.uniform(25.0, 30.0), 1)
        # humidity = round(random.uniform(40.0, 60.0), 1)
        
        # Symulacja regulacji pH
        if current_ph < target_ph:
            current_ph = round(current_ph + adjustment_rate, 2)
            adjustment_action = "Dodano zasade"
        elif current_ph > target_ph:
            current_ph = round(current_ph - adjustment_rate, 2)
            adjustment_action = "Dodano kwas"
        else:
            adjustment_action = "Brak dzialania"

        print(f"Symulacja Akwarium: Temp={temperature}C, pH={current_ph} ({adjustment_action})")

        # Zapis danych do bazy
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO water_control
            (temperature, ph, adjustment)
            VALUES (?, ?, ?)""",
            (temperature, current_ph, adjustment_action)
        )
        conn.commit()
        conn.close()

        # Odczyt co 10 sekund
        time.sleep(10)


# Funkcja symulujaca jakosc powietrza
def simulate_air_quality():
    """
    Symuluje jakość powietrza poprzez generowanie
    losowych wartości pomiarowych PM2.5, PM10, temperatury i wilgotności.
    Ocena jakości powietrza jest dokonywana na podstawie wartości PM2.5.
    Wartości pomiarowe są zapisywane do bazy danych co 10 sekund.
    Returns:
        None
    """

    while True:
        # Generowanie losowych wartosci pomiarowych
        pm25 = round(random.uniform(0.0, 100.0), 1)
        pm10 = round(random.uniform(0.0, 150.0), 1)
        temperature = round(random.uniform(15.0, 35.0), 1)
        humidity = round(random.uniform(30.0, 70.0), 1)

        # Ocena jako?ci powietrza na podstawie PM2.5
        if pm25 < 50:
            air_quality = "Dobra"
        elif pm25 < 100:
            air_quality = "Umiarkowana"
        else:
            air_quality = "Zla"

        print(f"""Symulacja Jakosci Powietrza:
              PM2.5={pm25} ug/m3, PM10={pm10} ug/m3,
              Temp={temperature}C, Wilgotnosc={humidity}%,
              Jakosc={air_quality}""")

        # Zapis danych do bazy
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO air_control
            (pm25, pm10, temperature, humidity, air_quality)
            VALUES (?, ?, ?, ?, ?)""",
            (pm25, pm10, temperature, humidity, air_quality)
        )
        conn.commit()
        conn.close()

        # Odczyt co 10 sekund
        time.sleep(10)


# Uruchomienie serwera Flask i symulacji sensora
if __name__ == '__main__':
    init_db(DB_PATH)

    ### WATKI SYMULUJACE ###

    # Wątek do symulacji sensora pH
    sensor_thread = threading.Thread(target=simulate_ph_control)
    sensor_thread.daemon = True
    sensor_thread.start()

    # Wątek do symulacji sensora
    sensor_thread = threading.Thread(target=simulate_sensor)
    sensor_thread.daemon = True
    sensor_thread.start()

    # Wątek do symulacji sensora jakości powietrza
    sensor_thread = threading.Thread(target=simulate_air_quality)
    sensor_thread.daemon = True
    sensor_thread.start()


    ### KONIEC WATKOW SYMULUJACYCH ###

    # Watek obslugujacy kamere
    camera_thread = threading.Thread(target=capture_camera)
    camera_thread.daemon = True
    camera_thread.start()

    # Wątek do detekcji ruchu
    motion_thread = threading.Thread(target=detect_motion)
    motion_thread.daemon = True
    motion_thread.start()

    # Uruchoemnie serwera Flask
    socketio.run(app, host='0.0.0.0', port=5000)
