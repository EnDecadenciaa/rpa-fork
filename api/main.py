from fastapi import FastAPI
from bot_recepcion.utils.loader import read_csv, insert_or_update_products
from bot_ventas.utils.loader import create_tables, insertar_orden
from bot_ventas.utils.stock_updater import actualizar_stock
from bot_ventas.utils.pdf_reader import leer_ordenes_de_pdfs

app = FastAPI()


@app.post("/bot_recepcion")
def run_recepcion():
    df = read_csv()
    if df is None:
        return {"status": "error", "message": "No se pudo leer el archivo CSV"}
    resultado = insert_or_update_products(df)
    print(f"[Bot Recepcion] Resultado: {resultado}")
    return {"status": "OK", "message": resultado}


@app.post("/bot_ventas")
def run_ventas():
    create_tables()
    ordenes = leer_ordenes_de_pdfs()

    for orden in ordenes:
        insertar_orden(orden)

    actualizar_stock()
    print(f"[Bot Ventas] Proceso completado correctamente.")
    return {"status": "OK", "message": "Órdenes cargadas y stock actualizado"}
