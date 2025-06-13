from db.db_connection import get_connection


def actualizar_stock(venta_id=None):
    conn = get_connection()
    if conn is None:
        print("Error al conectarse a la BD")
        return

    cursor = conn.cursor()

    try:
        if venta_id:
            # Get details only for the specified sale
            cursor.execute("""
                SELECT codigo_producto, cantidad 
                FROM detalle_venta 
                WHERE venta_id = ?
            """, (venta_id,))
        else:
            # Get the latest sale if no ID specified
            cursor.execute("""
                SELECT dv.codigo_producto, dv.cantidad 
                FROM detalle_venta dv
                JOIN ventas v ON v.id = dv.venta_id
                WHERE v.id = (SELECT MAX(id) FROM ventas)
            """)
        ventas = cursor.fetchall()

        for codigo_producto, cantidad_vendida in ventas:
            # Verificar stock actual
            cursor.execute(
                "SELECT cantidad FROM ingresos_productos WHERE codigo_producto = ?",
                (codigo_producto,),
            )
            result = cursor.fetchone()

            if result:
                stock_actual = result[0]
                nuevo_stock = max(
                    stock_actual - cantidad_vendida, 0
                )  # Evitar stock negativo

                cursor.execute(
                    """
                    UPDATE ingresos_productos
                    SET cantidad = ?
                    WHERE codigo_producto = ?
                """,
                    (nuevo_stock, codigo_producto),
                )

                print(
                    f"Codigo Producto: {codigo_producto}, stock actualizado {nuevo_stock}"
                )
            else:
                print(f"Producto con codigo {codigo_producto} no encontrado")

        conn.commit()

    except Exception as e:
        print(f"❌ Error al actualizar el stock: {e}")
    finally:
        conn.close()
