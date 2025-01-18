# Raspberry Pi Monitoring System

This project is designed to monitor various environmental conditions using sensors, process the data with Flask and FastAPI, and display results through a web interface. It integrates features like real-time weather monitoring, air quality control, pH level management for aquariums, and motion detection using a camera.

## Features

- **Weather Control**: Monitors temperature and humidity, storing and displaying the latest data.
- **Air Quality Control**: Tracks PM2.5, PM10 levels, air quality status, temperature, and humidity.
- **Water Control**: Monitors pH levels, temperature, and performs adjustments for maintaining the right pH.
- **Camera Streaming**: Captures video using a Raspberry Pi camera and streams it live.
- **Motion Detection**: Detects motion through the camera, captures images, and stores them.
- **WebSocket Communication**: Allows real-time updates to the front-end on measurement changes, motion detection, and other alerts.

## Technologies

- **Flask**: Web framework for creating REST APIs and handling web pages.
- **FastAPI**: A faster alternative to Flask for building asynchronous APIs.
- **SQLite**: Lightweight database for storing sensor data and measurements.
- **OpenCV**: Used for capturing video and detecting motion.
- **SocketIO**: Real-time bi-directional communication for front-end updates.
- **Threads**: Used for simulating sensor data, camera capture, and motion detection without blocking the main application.

## Setup

### Prerequisites

- Python (>= 3.8)
- Raspberry Pi or a similar device with a camera.

### Dependencies

Install required packages via pip:

```bash
pip install flask fastapi flask-socketio opencv-python sqlite3
```

### Running the Application

Clone the repository:

```bash
git clone <repository-url>
cd <repository-directory>
```

Initialize the SQLite database (if not already created):

```python
python app.py
```

Start the Flask application:

```bash
python app.py
```

The server will run on `http://0.0.0.0:5000/`.

### FastAPI Integration

In addition to Flask, FastAPI is also implemented for handling asynchronous requests for better performance. You can run the FastAPI app separately by using:

```bash
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

## Endpoints

### Weather Data

- `GET /weather`: Fetch the latest 10 weather measurements (temperature, humidity).

### Air Quality Data

- `GET /air`: Fetch the latest 10 air quality measurements (PM2.5, PM10, temperature, humidity, air quality status).

### Water Control Data

- `GET /water`: Fetch the latest 10 water control measurements (pH, temperature, adjustment action).

### Camera Streaming

- `GET /video_feed`: Stream video from the Raspberry Pi camera.

### Historical Data

- `GET /history`: Fetch all weather measurements in history.

### Alerts

- `POST /alert`: Set alert thresholds for temperature and humidity.

## Web Interface

The application provides several pages:

- **Landing Page**: Displays the main page with options to view different sensors' data.
- **Weather Page**: Displays the latest weather measurements.
- **Air Quality Page**: Displays the air quality data.
- **Water Control Page**: Displays the latest pH control data.
- **Camera Page**: Displays the camera feed and alerts when motion is detected.

## Motion Detection

The system continuously monitors for motion via the camera. When motion is detected, an image is captured, saved locally, and sent to the front-end through WebSocket. It uses OpenCV to compare consecutive frames and detect significant changes.

## Database Schema

The system uses an SQLite database to store measurements. There are tables for:

- `weather_control`: Stores temperature and humidity.
- `air_control`: Stores PM2.5, PM10, air quality, temperature, and humidity.
- `water_control`: Stores pH levels, temperature, and adjustment actions.

## Simulated Data

To simulate sensor readings for testing, the following functions are available:

- `simulate_sensor`: Simulates temperature and humidity data.
- `simulate_ph_control`: Simulates pH control data for an aquarium.
- `simulate_air_quality`: Simulates air quality data (PM2.5, PM10, temperature, and humidity).