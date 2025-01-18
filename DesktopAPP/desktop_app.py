""" Desktopowa aplikacja pobierająca dane z API serwera RPI5 """

import tkinter as tk
from tkinter import messagebox
import requests

# Adres API serwera Flask
API_URL = 'http://192.168.0.18:5000'  # Zmienna na adres IP Raspberry Pi


def fetch_air():
    """ Funkcja pobierająca API pomiarów powietrza """
    try:
        response = requests.get(f'{API_URL}/air')
        if response.status_code == 200:
            data = response.json()
            open_listbox.delete(0, tk.END)
            for measurement in data:
                open_listbox.insert(tk.END,
                f"""ID: {measurement['id']},
                timestamp: {measurement['timestamp']}
                Temp: {measurement['temperature']}°C,
                Humidity: {measurement['humidity']}%
                pm2.5: {measurement['pm25']} ug/m3
                pm10: {measurement['pm10']} ug/m3
                """)
        else:
            messagebox.showerror("Błąd", "Nie udało się pobrać pomiarów")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Błąd", f"Wystąpił problem z połączeniem: {e}")

def fetch_water():
    """ Funkcja do pobierania API pomiarów wody """
    try:
        response = requests.get(f'{API_URL}/water')
        if response.status_code == 200:
            data = response.json()
            open_listbox.delete(0, tk.END)
            for measurement in data:
                open_listbox.insert(tk.END,
                f"""ID: {measurement['id']}
                Time: {measurement['timestamp']}
                Temp: {measurement['temperature']}°C
                Zmierzone PH: {measurement['ph']}
                """)
        else:
            messagebox.showerror("Błąd", "Nie udało się pobrać historii")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Błąd", f"Wystąpił problem z połączeniem: {e}")

def fetch_weather():
    """ Funkcja do pobierania API pomiarów pogody """
    try:
        response = requests.get(f'{API_URL}/weather')
        if response.status_code == 200:
            data = response.json()
            open_listbox.delete(0, tk.END)
            for measurement in data:
                open_listbox.insert(tk.END,
                f"""ID: {measurement['id']}
                Time: {measurement['timestamp']}
                Temp: {measurement['temperature']}°C
                Wilgotność: {measurement['humidity']}
                """)
        else:
            messagebox.showerror("Błąd", "Nie udało się pobrać historii")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Błąd", f"Wystąpił problem z połączeniem: {e}")

def close_app():
    """Funkcja do zamknięcia aplikacji."""
    root.quit()


def fetch_error():
    """ Funkcja do pobierania API pomiarów pogody """
    try:
        response = requests.get(f'{API_URL}/error')
        if response.status_code == 200:
            data = response.json()
            open_listbox.delete(0, tk.END)
            for measurement in data:
                open_listbox.insert(tk.END,
                measurement['error'])
        else:
            messagebox.showerror("Błąd", "Nie udało się pobrać historii")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Błąd", f"Wystąpił problem z połączeniem: {e}")

# Tworzenie głównego okna Tkinter
root = tk.Tk()
root.title("Aplikacja Pomiarowa działająca na API Raspberry Pi")

# Lista pomiarów
open_listbox = tk.Listbox(root, width=180, height=10)
open_listbox.pack(pady=10)

# Przycisk do pobierania pomiarów pogody
fetch_measurements_button = tk.Button(root, text="Pobierz Pomiary Pogodowe", command=fetch_weather)
fetch_measurements_button.pack(pady=5)

# Przycisk do pobierania pomiarów powietrza
fetch_measurements_button = tk.Button(root, text="Pobierz Pomiary Powietrza", command=fetch_air)
fetch_measurements_button.pack(pady=5)

# Przycisk do pobierania pomiarów wody
fetch_water_button = tk.Button(root, text="Pobierz Pomiary Wody", command=fetch_water)
fetch_water_button.pack(pady=5)

# Tworzenie guzika "Exit"
exit_button = tk.Button(root, text="Exit", command=close_app)
exit_button.pack(pady=20)


### STREFA TESTOWA ###

# Separator
separator = tk.Label(root,
                     text="test zone",
                     height=1, bg="black",
                     fg="white", width=40)
separator.pack(pady=10)

# Przycisk do pobierania pomiarów wody
fetch_error_button = tk.Button(root,
                            text="Guzik error",
                            bg="#ff6347",
                            fg="white",
                            command=fetch_error)
fetch_error_button.pack(pady=5)


# Uruchomienie głównej pętli Tkinter
root.mainloop()
