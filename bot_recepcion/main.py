import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.loader import read_csv, insert_or_update_products


def run_bot_recepcion():
    print("[Bot Recepcion] Iniciando proceso de carga de productos.")

    df = read_csv()
    if df is None:
        print("[Bot Recepecion] Error: no se pudo leer el archivo CSV")
        return

    resultado = insert_or_update_products(df)
    print(f"[Bot Recepcion] Resultado: {resultado}")


if __name__ == "__main__":
    run_bot_recepcion()
