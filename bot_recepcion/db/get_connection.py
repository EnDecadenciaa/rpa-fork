# db.py
import sqlite3
from config import db_path

def get_connection():
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"Error de conexión a la base de datos: {e}")
        return None
