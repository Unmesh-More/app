# database.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'fishnav.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS spots (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT,
            lat      REAL,
            lon      REAL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS routes (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            lat      REAL,
            lon      REAL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_spot_to_db(name, lat, lon):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO spots (name, lat, lon) VALUES (?, ?, ?)',
              (name, lat, lon))
    conn.commit()
    conn.close()

def get_all_spots():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, lat, lon, saved_at FROM spots ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def save_route_point(lat, lon):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO routes (lat, lon) VALUES (?, ?)', (lat, lon))
    conn.commit()
    conn.close()