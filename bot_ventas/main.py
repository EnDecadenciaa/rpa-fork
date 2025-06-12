import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.loader import create_tables, insertar_orden
from utils.pdf_reader import leer_ordenes_de_pdfs
from utils.stock_updater import actualizar_stock

def main():
    create_tables()
    ordenes = leer_ordenes_de_pdfs()
    for orden in ordenes:
        insertar_orden(orden)
        print(f"Orden {orden['nro_orden']} procesada")
        
        
if __name__ == "__main__":
    main()
    actualizar_stock()