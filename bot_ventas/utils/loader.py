from db.db_connection import get_connection


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nro_orden TEXT,
            cliente TEXT,
            fecha TEXT
        )"""
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS detalle_venta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER,
            codigo_producto TEXT,
            cantidad INTEGER,
            FOREIGN KEY (venta_id) REFERENCES ventas(id)
        )"""
    )

    conn.commit()
    conn.close()


def insertar_orden(orden):
    conn = get_connection()
    cursor = conn.cursor()

    # Verificamos si ya existe la orden
    cursor.execute("SELECT 1 FROM ventas WHERE nro_orden = ?", (orden['nro_orden'],))
    if cursor.fetchone():
        print(f"⚠️ Orden {orden['nro_orden']} ya existe. Se omite.")
        return

    # Insertar venta
    cursor.execute(
        "INSERT INTO ventas (nro_orden, cliente, fecha) VALUES (?, ?, ?)",
        (orden["nro_orden"], orden["cliente"], orden["fecha"]),
    )

    venta_id = cursor.lastrowid

    for producto in orden["productos"]:
        cursor.execute(
            "INSERT INTO detalle_venta (venta_id, codigo_producto, cantidad) VALUES (?, ?, ?)",
            (venta_id, producto["codigo"], producto["cantidad"]),
        )
    
    conn.commit()
    conn.close()