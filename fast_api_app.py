""" Fast Api version of the project """
# Standard library imports
import os
from datetime import datetime
import sqlite3
import threading
import time
import random

# Third-party imports
import cv2
import socketio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles


# Konfiguracja FastAPI
app=FastAPI()
sio=socketio.AsyncServer(async_mode='asgi')
app.add_route("/socket.io/", socketio.ASGIApp(sio))

# Global variable to store the last frame
camera_lock=Lock()
LAST_FRAME=None

# Konfiguracja bazy danych
base_dir=os.path.dirname(os.path.abspath(__file__))
db_path=os.path.join(base_dir, "measurements.db")

templates=Jinja2Templates(
    directory="/home/raspi/Desktop/ProjektZaliczeniowy/Projekt/templates")
app.mount("/static", StaticFiles(
    directory="/home/raspi/Desktop/ProjektZaliczeniowy/Projekt/static"),
    name="static")


# Inicjalizacja bazy danych
def init_db(db_path):
    """Inicjalizacja bazy danych."""
    if not os.path.exists(db_path):
        print("Baza danych nie istnieje. Tworze nowa...")

    try:
        conn=sqlite3.connect(db_path)
        cursor=conn.cursor()

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
    except ValueError as e:
        print(f"Wystapil blad podczas inicjalizacji bazy danych: {e}")

# Kamerka - generowanie klatek
def capture_camera():
    """Obsluguje kamere, odczytujac klatki i zapisujac je do globalnej zmiennej."""
    global LAST_FRAME
    try:
        camera=cv2.VideoCapture(0)

        if not camera.isOpened():
            raise RuntimeError("Nie mozna uzyskac dostepu do kamery.")

        while True:
            success, frame=camera.read()
            if not success:
                break

            with camera_lock:
                LAST_FRAME=frame.copy()  # Aktualizuj globalna klatke

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
            _, buffer=cv2.imencode('.jpg', LAST_FRAME)
            frame=buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def detect_motion():
    """Wykrywa ruch na podstawie najnowszych klatek,
    zapisuje zdjecie i rysuje kwadrat wokol wykrytego ruchu."""
    global LAST_FRAME
    prev_frame_gray=None

    photo_dir="/home/raspi/Desktop/ProjektZaliczeniowy/Projekt/phototrap/fast_api"

    # Upewnij sie, ze folder istnieje
    if not os.path.isdir(photo_dir):
        print(f"Tworzenie katalogu {photo_dir}")
        os.makedirs(photo_dir)

    while True:
        with camera_lock:
            if LAST_FRAME is None:
                continue
            frame=LAST_FRAME.copy()

        # Przetwarzanie klatki
        gray_frame=cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame=cv2.GaussianBlur(gray_frame, (21, 21), 0)

        if prev_frame_gray is None:
            prev_frame_gray=gray_frame
            continue

        # Analiza roznic miedzy klatkami
        frame_delta=cv2.absdiff(prev_frame_gray, gray_frame)
        _, thresh=cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
        thresh=cv2.dilate(thresh, None, iterations=2)

        # Znajdz kontury
        contours, _=cv2.findContours(thresh.copy(),
                                       cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        motion_detected=False

        for contour in contours:
            if cv2.contourArea(contour) > 25000:
                motion_detected=True

                # Rysowanie prostokata wokol konturu
                (x, y, w, h)=cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if motion_detected:
            print("Ruch wykryty!")
            # Przeslij zdarzenie o wykryciu ruchu do klientow
            sio.emit('motion', {'status': 'motion_detected'})

            # Zapisz zdjecie
            timestamp=datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
            filename=os.path.join(photo_dir, f"picture_{timestamp}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Zdjecie zapisane jako {filename}")

            # Czekaj 10 sekund przed nastepnym zapisem
            time.sleep(10)

        prev_frame_gray=gray_frame
        time.sleep(0.1)  # Unikaj przeciazenia CPU

@sio.event
async def connect(sid):
    """
    Nawiązuje połączenie z klientem.
    Parametry:
    - sid (str): Identyfikator sesji klienta.
    - environ (dict): Słownik zawierający informacje o środowisku.
    Zadaniem tej funkcji jest nawiązanie połączenia z
    klientem i wyświetlenie informacji o nawiązanym połączeniu.
    Przykład użycia:
        connect('abc123', {'key': 'value'})
    """

    print(f"Połączenie nawiązane: {sid}")

@sio.event
async def disconnect(sid):
    """
    Funkcja asynchroniczna odpowiedzialna za zakończenie połączenia.
    :param sid: Identyfikator sesji połączenia.
    """

    print(f"Połączenie zakończone: {sid}")

@app.on_event("startup")
def startup_event():
    """
    Funkcja inicjalizująca aplikację i uruchamiająca wątki do symulacji danych oraz obsługi kamery.
    Inicjalizuje bazę danych.
    Tworzy wątki do symulacji kontroli pH, czujnika oraz jakości powietrza.
    Tworzy wątek do obsługi kamery.
    Uruchamia funkcję wykrywania ruchu i kamery w tle.
    """

    init_db(db_path)

    # Watki do symulacji danych
    sensor_thread=threading.Thread(target=simulate_ph_control)
    sensor_thread.daemon=True
    sensor_thread.start()

    sensor_thread=threading.Thread(target=simulate_sensor)
    sensor_thread.daemon=True
    sensor_thread.start()

    sensor_thread=threading.Thread(target=simulate_air_quality)
    sensor_thread.daemon=True
    sensor_thread.start()

    # Watek do obslugi kamery
    camera_thread=threading.Thread(target=capture_camera)
    camera_thread.daemon=True
    camera_thread.start()

    # Uruchom funkcje wykrywania ruchu i kamery w tle
    thread_camera=threading.Thread(target=capture_camera)
    thread_camera.daemon=True
    thread_camera.start()

    thread_motion=threading.Thread(target=detect_motion)
    thread_motion.daemon=True
    thread_motion.start()

# Strona glowna
@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """
    Obsługuje żądanie strony głównej.
    Parametry:
    - request (Request): Obiekt żądania.
    Zwraca:
    - templates.TemplateResponse: Obiekt odpowiedzi z szablonem strony głównej.
    """

    return templates.TemplateResponse("index.html", {"request": request})

# Strona z pomiarami
@app.get("/measurements_page", response_class=HTMLResponse)
async def measurements_page(request: Request):
    """
    Funkcja obsługująca stronę z pomiarami.
    Parametry:
    - request (Request): Obiekt żądania HTTP.
    Zwraca:
    - TemplateResponse: Obiekt odpowiedzi HTTP zawierający szablon HTML z pomiarami.
    """

    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM weather_control ORDER BY timestamp DESC LIMIT 10")
    measurements=cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("measurements.html",
                                      {"request": request,
                                       "measurements": measurements})

# Strona z historia
@app.get("/history_page", response_class=HTMLResponse)
async def history_page(request: Request):
    """
    Funkcja obsługująca stronę historii pomiarów.
    Parametry:
    - request (Request): Obiekt żądania HTTP.
    Zwracane wartości:
    - templates.TemplateResponse: Obiekt odpowiedzi HTTP
    zawierający szablon HTML "measurements.html" wraz z danymi pomiarów.
    Wyjątki:
    - Brak.
    Opis:
    Ta funkcja obsługuje żądanie HTTP dotyczące strony historii
    pomiarów. Łączy się z bazą danych, pobiera wszystkie pomiary
    z tabeli "weather_control" posortowane według znacznika czasowego,
    zamyka połączenie z bazą danych, a następnie zwraca odpowiedź HTTP
    zawierającą szablon HTML "measurements.html" wraz z danymi pomiarów.
    """

    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM weather_control ORDER BY timestamp")
    measurements=cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("measurements.html",
                                      {"request": request,
                                       "measurements": measurements})

# Strona z kamera
@app.get("/door_bell_page", response_class=HTMLResponse)
async def door_bell_page(request: Request):
    """
    Obsługuje żądanie strony dzwonka do drzwi.
    Parametry:
    - request (Request): Obiekt żądania HTTP.
    Zwraca:
    - templates.TemplateResponse: Obiekt odpowiedzi HTTP z szablonem strony kamery.
    """

    return templates.TemplateResponse("camera.html", {"request": request})

# Strona z aquarium
@app.get("/aquarium", response_class=HTMLResponse)
async def ph_measurements_page(request: Request):
    """
    Funkcja zwraca strone z pomiarami pH.
    :param request: Obiekt zadania HTTP.
    :return: Szablon HTML strony z pomiarami pH.
    """
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()
    cursor.execute("""
                   SELECT id, timestamp, temperature, ph, adjustment
                   FROM water_control
                   ORDER BY timestamp DESC LIMIT 20
                   """)
    measurements=cursor.fetchall()
    conn.close()

    # Renderowanie szablonu HTML z pomiarami
    return templates.TemplateResponse("aquarium.html", {
        "request": request,
        "measurements": measurements
    })

@app.get("/air_quality", response_class=HTMLResponse)
async def air_quality_page(request: Request):
    """
    Funkcja zwraca strone z pomiarami jakosci powietrza.
    :param request: Obiekt zadania HTTP.
    :return: Szablon HTML strony z pomiarami jakosci powietrza.
    """
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()
    cursor.execute("""
                   SELECT id, timestamp, temperature,
                   pm25, pm10, humidity, air_quality 
                   FROM air_control 
                   ORDER BY timestamp DESC LIMIT 20
                   """)
    measurements=cursor.fetchall()
    conn.close()

    # Renderowanie szablonu HTML z pomiarami
    return templates.TemplateResponse("air_quality.html", {
        "request": request,
        "measurements": measurements
    })

# Strumien wideo
@app.get("/video_feed")
async def video_feed():
    """Zwraca strumien wideo z kamery."""
    return StreamingResponse(generate_frames(),
                media_type='multipart/x-mixed-replace; boundary=frame')

@app.get("/latest_frame")
async def get_latest_frame():
    """Zwraca najnowsza klatke jako obraz JPG."""
    with camera_lock:
        if LAST_FRAME is not None:
            _, encoded_img=cv2.imencode('.jpg', LAST_FRAME)
            return {"image": encoded_img.tobytes()}
        return {"message": "No frame available"}

# Symulacja sensora
def simulate_sensor():
    """Symuluje pomiary z czujnika."""
    while True:
        temperature=round(random.uniform(20.0, 30.0), 1)
        humidity=round(random.uniform(40.0, 60.0), 1)
        print(f"Symulacja: Temp={temperature}C, Wilgotnosc={humidity}%")
        conn=sqlite3.connect(db_path)
        cursor=conn.cursor()
        cursor.execute("""INSERT INTO weather_control
                       (temperature, humidity)
                       VALUES (?, ?)""",
                       (temperature, humidity))
        conn.commit()
        conn.close()
        time.sleep(10)

# Funkcja symulujaca kontrole pH
def simulate_ph_control():
    """Symuluje kontrole pH w akwarium."""
    target_ph=7.0
    adjustment_rate=0.1
    while True:
        current_ph=round(random.uniform(6.0, 8.0), 2)
        temperature=round(random.uniform(25.0, 30.0), 1)
        if current_ph < target_ph:
            current_ph=round(current_ph + adjustment_rate, 2)
            adjustment_action="Dodano zasade"
        elif current_ph > target_ph:
            current_ph=round(current_ph - adjustment_rate, 2)
            adjustment_action="Dodano kwas"
        else:
            adjustment_action="Brak dzialania"
        print(f"""Symulacja Akwarium:
              Temp={temperature}C,
              pH={current_ph}
              ({adjustment_action})""")
        conn=sqlite3.connect(db_path)
        cursor=conn.cursor()
        cursor.execute("""INSERT INTO water_control
                       (temperature, ph, adjustment)
                       VALUES (?, ?, ?)""",
                       (temperature, current_ph, adjustment_action))
        conn.commit()
        conn.close()
        time.sleep(10)

# Symulacja jakosci powietrza
def simulate_air_quality():
    """Symuluje pomiary jakosci powietrza."""
    while True:
        pm25=round(random.uniform(0.0, 100.0), 1)
        pm10=round(random.uniform(0.0, 150.0), 1)
        temperature=round(random.uniform(15.0, 35.0), 1)
        humidity=round(random.uniform(30.0, 70.0), 1)
        air_quality="Dobra" if pm25 < 50 else "Umiarkowana" if pm25 < 100 else "Zla"
        print(f"""Symulacja Jakosci Powietrza:
              PM2.5={pm25},
              PM10={pm10},
              Temp={temperature}C,
              Wilgotnosc={humidity}%,
              Jakosc={air_quality}""")
        conn=sqlite3.connect(db_path)
        cursor=conn.cursor()
        cursor.execute("""INSERT INTO air_control
                       (pm25, pm10, temperature, humidity, air_quality)
                       VALUES (?, ?, ?, ?, ?)""",
                       (pm25, pm10, temperature, humidity, air_quality))
        conn.commit()
        conn.close()
        time.sleep(10)

# Uruchomienie serwera FastAPI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
