import sqlite3

def view_database():
    conn = sqlite3.connect('db/productos.db')
    cursor = conn.cursor()
    
    print("\n=== PRODUCTOS EN INVENTARIO ===")
    cursor.execute('SELECT * FROM ingresos_productos')
    products = cursor.fetchall()
    for product in products:
        print(f"Código: {product[1]}")
        print(f"Descripción: {product[2]}")
        print(f"Cantidad: {product[3]}")
        print(f"Fecha: {product[4]}")
        print(f"Proveedor: {product[5]}")
        print("-" * 40)
    
    print("\n=== ÓRDENES DE VENTA ===")
    cursor.execute('SELECT v.*, dv.codigo_producto, dv.cantidad FROM ventas v JOIN detalle_venta dv ON v.id = dv.venta_id')
    orders = cursor.fetchall()
    current_order = None
    for order in orders:
        if current_order != order[1]:  # new order
            current_order = order[1]
            print(f"\nOrden N°: {order[1]}")
            print(f"Cliente: {order[2]}")
            print(f"Fecha: {order[3]}")
            print("Productos:")
        print(f"- {order[4]}: {order[5]} unidades")
    
    conn.close()

if __name__ == "__main__":
    view_database()
