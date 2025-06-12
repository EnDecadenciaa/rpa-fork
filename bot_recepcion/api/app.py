from fastapi import FastAPI
from utils.loader import read_csv, insert_or_update_products

app = FastAPI()


@app.post("/run-bot")
def run_bot():
    df = read_csv()
    if df is None:
        return {"status": "error", "message": "No se pudo leer el archivo CSV"}

    resultado = insert_or_update_products(df)
    print(f"[Bot Recepcion] Resultado: {resultado}")

    return {"status": "OK", "message": resultado}
