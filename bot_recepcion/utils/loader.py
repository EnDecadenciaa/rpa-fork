import pandas as pd
from db.get_connection import get_connection
from config import url_csv

def read_csv():

    try:
        #Leer csv desde google sheets
        df = pd.read_csv(url_csv)
        
        #eliminar columna id si esta presente
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
        
        return df
    except Exception as e:
        print(f"Error al leer el csv: {e}")
        return None

def ensure_table_exists():
    conn = get_connection()
    if conn is None:
        print("[DB] No se pudo conectar a la base de datos.")
        return

    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ingresos_productos (
                codigo_producto TEXT PRIMARY KEY,
                descripcion TEXT,
                cantidad INTEGER,
                fecha_ingreso TEXT,
                proveedor TEXT
            )
        ''')
        conn.commit()
        print("[DB] Tabla 'ingresos_productos' verificada o creada.")
    except Exception as e:
        print(f"[DB] Error al verificar/crear tabla: {e}")
    finally:
        conn.close()


def insert_or_update_products(df):
    #Verificar la existencia de la tabla antes de insertar
    ensure_table_exists()
    
    conn = get_connection()
    if conn is None:
        return "No se pudo conectar a la BD"
    
    cursor = conn.cursor()
    insertados = 0
    actualizados = 0
    
    try:
        for _, row in df.iterrows():
            codigo = row['codigo_producto']
            descripcion = row['descripcion']
            cantidad = row['cantidad']
            fecha = row['fecha_ingreso']
            proveedor = row['proveedor']
        
            #Verificar si ya existe el producto
            cursor.execute("SELECT cantidad FROM ingresos_productos WHERE codigo_producto = ?", (codigo,))
            result = cursor.fetchone()
            
            if result:
                cantidad_actual = result[0]
                nueva_cantidad = cantidad_actual + cantidad
                cursor.execute("""
                    UPDATE ingresos_productos
                    SET cantidad = ?, descripcion = ?, fecha_ingreso = ?, proveedor = ?
                    WHERE codigo_producto = ?
                """, (nueva_cantidad, descripcion, fecha, proveedor, codigo))
                actualizados += 1
            else:
                cursor.execute("""
                    INSERT INTO ingresos_productos (codigo_producto, descripcion, cantidad, fecha_ingreso, proveedor)
                    VALUES (?, ?, ?, ?, ?)
                """, (codigo, descripcion, cantidad, fecha, proveedor))
                insertados += 1
        conn.commit()
        return f"Productos Insertados: {insertados}, Actualizados {actualizados}"
    except Exception as e:
        return f"Error al insertar/actualizar productos: {e}"
    finally:
        conn.close()