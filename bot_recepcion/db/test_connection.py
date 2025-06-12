import os
import sqlite3
from config import db_path

# Verificar si el archivo existe
if not os.path.exists(db_path):
    print("❌ El archivo de la base de datos no existe.")
else:
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")  # Ejecuta una consulta simple
        print("✅ Conexión a la base de datos exitosa.")
        conn.close()
    except sqlite3.Error as e:
        print(f"❌ Error al conectarse a la base de datos: {e}")
