import fitz
import os

PDFS_DIR = "bot_ventas/pdfs"

def leer_texto_pdf(ruta_pdf):
    doc = fitz.open(ruta_pdf)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    doc.close()
    return texto

def extraer_orden_desde_text(texto):
    lineas = texto.strip().split("\n")
    orden = {
        "nro_orden": None,
        "cliente": None,
        "fecha": None,
        "productos": []
    }
    for linea in lineas:
        if "Orden N°" in linea:
            orden["nro_orden"] = linea.split(":")[1].strip()
        elif "Cliente:" in linea:
            orden["cliente"] = linea.split(":")[1].strip()
        elif "Fecha:" in linea:
            orden["fecha"] = linea.split(":")[1].strip()
        elif "Código:" in linea:
            partes = linea.split("|")
            cod = partes[0].split(":")[1].strip()
            nombre = partes[1].split(":")[1].strip()
            cantidad = int(partes[2].split(":")[1].strip())
            orden["productos"].append({
                "codigo": cod,
                "nombre": nombre,
                "cantidad": cantidad
            })
    return orden

def leer_ordenes_de_pdfs():
    ordenes = []
    for archivo in os.listdir(PDFS_DIR):
        if archivo.endswith(".pdf"):
            ruta = os.path.join(PDFS_DIR, archivo)
            try:
                texto = leer_texto_pdf(ruta)
                orden = extraer_orden_desde_text(texto)
                ordenes.append(orden)
            except Exception as e:
                print(f"Error procesando {archivo}: {e}")
    
    return ordenes
        