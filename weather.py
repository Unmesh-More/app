# weather.py
# FishNav Weather Module — Built for Indian fishermen
# Uses OpenWeatherMap API with offline cache support

import requests
import json
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'fishnav.db')

# ─── PASTE YOUR API KEY HERE ───────────────────────────────
API_KEY = '5e10c23aefdb6e0c1a46fe4d9c47e1db'
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'

# second key 1b7bef774b502c707484e505bd042452
# ─── CACHE ─────────────────────────────────────────────────
def init_weather_cache():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS weather_cache (
            id         INTEGER PRIMARY KEY,
            city       TEXT UNIQUE,
            data       TEXT,
            fetched_at TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_to_cache(city, data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO weather_cache (city, data, fetched_at)
        VALUES (?, ?, ?)
        ON CONFLICT(city) DO UPDATE SET
            data=excluded.data,
            fetched_at=excluded.fetched_at
    ''', (city.lower(), json.dumps(data), datetime.now().strftime('%d %b %Y, %I:%M %p')))
    conn.commit()
    conn.close()


def load_from_cache(city):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT data, fetched_at FROM weather_cache WHERE city = ?',
              (city.lower(),))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0]), row[1]
    return None, None


# ─── INTERNET CHECK ────────────────────────────────────────
def is_connected():
    try:
        requests.get('https://openweathermap.org', timeout=3)
        return True
    except Exception:
        return False


# ─── FETCH WEATHER ─────────────────────────────────────────
def fetch_weather(city):
    """
    Returns (data_dict, is_live, fetched_at) or (None, False, None)
    """
    if is_connected():
        try:
            response = requests.get(BASE_URL, params={
                'q':     city,
                'appid': API_KEY,
                'units': 'metric'
            }, timeout=5)

            if response.status_code == 200:
                raw = response.json()

                # Parse into clean fisherman-friendly dict
                data = {
                    'city':        raw['name'],
                    'country':     raw['sys']['country'],
                    'temperature': round(raw['main']['temp']),
                    'feels_like':  round(raw['main']['feels_like']),
                    'humidity':    raw['main']['humidity'],
                    'description': raw['weather'][0]['description'].title(),
                    'wind_speed':  round(raw['wind']['speed'] * 3.6),  # m/s to km/h
                    'wind_deg':    raw['wind'].get('deg', 0),
                    'wind_dir':    deg_to_compass(raw['wind'].get('deg', 0)),
                    'rain_1h':     raw.get('rain', {}).get('1h', 0),
                    'sunrise':     unix_to_time(raw['sys']['sunrise']),
                    'sunset':      unix_to_time(raw['sys']['sunset']),
                }

                save_to_cache(city, data)
                return data, True, datetime.now().strftime('%d %b %Y, %I:%M %p')

        except Exception as e:
            print(f'Weather API error: {e}')

    # Offline fallback
    data, fetched_at = load_from_cache(city)
    if data:
        return data, False, fetched_at

    return None, False, None


# ─── HELPER FUNCTIONS ──────────────────────────────────────
def deg_to_compass(deg):
    """Convert wind degree to compass direction."""
    dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    ix = round(deg / 45) % 8
    return dirs[ix]


def unix_to_time(unix_ts):
    """Convert Unix timestamp to readable time."""
    return datetime.fromtimestamp(unix_ts).strftime('%I:%M %p')


def wind_advice(speed):
    """Give simple fishing advice based on wind speed."""
    if speed < 15:
        return '✅ Safe to fish'
    elif speed < 30:
        return '⚠️ Fish with caution'
    else:
        return '🚫 Too windy — stay ashore'

def fetch_weather_by_coords(lat, lon):
    """
    Fetch weather using GPS coordinates directly.
    Returns (data_dict, is_live, fetched_at) or (None, False, None)
    """
    if is_connected():
        try:
            response = requests.get(BASE_URL, params={
                'lat':   lat,
                'lon':   lon,
                'appid': API_KEY,
                'units': 'metric'
            }, timeout=5)

            if response.status_code == 200:
                raw = response.json()
                city = raw['name']

                data = {
                    'city':        city,
                    'country':     raw['sys']['country'],
                    'temperature': round(raw['main']['temp']),
                    'feels_like':  round(raw['main']['feels_like']),
                    'humidity':    raw['main']['humidity'],
                    'description': raw['weather'][0]['description'].title(),
                    'wind_speed':  round(raw['wind']['speed'] * 3.6),
                    'wind_deg':    raw['wind'].get('deg', 0),
                    'wind_dir':    deg_to_compass(raw['wind'].get('deg', 0)),
                    'rain_1h':     raw.get('rain', {}).get('1h', 0),
                    'sunrise':     unix_to_time(raw['sys']['sunrise']),
                    'sunset':      unix_to_time(raw['sys']['sunset']),
                }

                save_to_cache(city, data)
                return data, True, datetime.now().strftime('%d %b %Y, %I:%M %p')

        except Exception as e:
            print(f'Weather API error: {e}')

    # Offline fallback using last cached city
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT data, fetched_at FROM weather_cache ORDER BY rowid DESC LIMIT 1')
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0]), False, row[1]

    return None, False, None