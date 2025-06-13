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
    cursor.execute("SELECT id FROM ventas WHERE nro_orden = ?", (orden['nro_orden'],))
    existing = cursor.fetchone()
    if existing:
        print(f"⚠️ Orden {orden['nro_orden']} ya existe. Se omite.")
        return existing[0]  # Return existing order ID

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
    order_id = venta_id  # Use the venta_id we already have
    conn.close()
    return order_id