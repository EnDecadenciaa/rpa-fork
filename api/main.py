from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from bot_recepcion.utils.loader import read_csv, insert_or_update_products
from bot_ventas.utils.loader import create_tables, insertar_orden
from bot_ventas.utils.stock_updater import actualizar_stock
from bot_ventas.utils.pdf_reader import leer_ordenes_de_pdfs
from db.db_connection import get_connection
from datetime import datetime
import os
import traceback
from fpdf import FPDF
from pathlib import Path

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()

# Mount static files with absolute path
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Setup templates with absolute path
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        print("Attempting to connect to database...")
        # Get products from database
        conn = get_connection()
        if conn is None:
            print("Failed to connect to database")
            return HTMLResponse(content="Database connection failed", status_code=500)
        cursor = conn.cursor()
        cursor.execute('SELECT codigo_producto, descripcion, cantidad FROM ingresos_productos')
        products = cursor.fetchall()
        print(f"Found {len(products)} products")
        conn.close()
        
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "products": products}
        )
    except Exception as e:
        print(f"Error in home route: {str(e)}")
        return JSONResponse(
            {"status": "error", "message": "Error loading products"},
            status_code=500
        )


@app.post("/create_order")
async def create_order(request: Request):
    try:
        print("Starting order creation...")
        form_data = await request.form()
        print(f"Received form data: {dict(form_data)}")
        order_items = []
        
        # Process form data
        cliente = form_data.get("cliente")
        if not cliente:
            return JSONResponse({"status": "error", "message": "Cliente es requerido"}, status_code=400)
            
        orden_num = datetime.now().strftime("%Y%m%d%H%M%S")  # Unique order number
        
        # Ensure PDFs directory exists
        pdf_dir = os.path.join('bot_ventas', 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Orden N°: {orden_num}', ln=True)
        pdf.cell(0, 10, f'Cliente: {cliente}', ln=True)
        pdf.cell(0, 10, f'Fecha: {current_date}', ln=True)
        
        has_products = False
        # Process selected products
        conn = get_connection()
        cursor = conn.cursor()
        
        # Insert order into ventas table first
        cursor.execute(
            "INSERT INTO ventas (nro_orden, cliente, fecha) VALUES (?, ?, ?)",
            (orden_num, cliente, current_date)
        )
        venta_id = cursor.lastrowid
        
        # Initialize order_items list for later use
        order_items = []
        
        for key in form_data.keys():
            if key.startswith('cantidad_'):
                producto_id = key.replace('cantidad_', '')
                try:
                    cantidad = int(form_data[key])
                    if cantidad > 0:
                        # Get product description for the PDF
                        cursor.execute(
                            "SELECT descripcion FROM ingresos_productos WHERE codigo_producto = ?",
                            (producto_id,)
                        )
                        descripcion = cursor.fetchone()[0]
                        
                        pdf.cell(0, 10, f'Código: {producto_id} | Descripción: {descripcion} | Cantidad: {cantidad}', ln=True)
                        
                        # Insert order detail
                        cursor.execute(
                            "INSERT INTO detalle_venta (venta_id, codigo_producto, cantidad) VALUES (?, ?, ?)",
                            (venta_id, producto_id, cantidad)
                        )
                        
                        # Add to order_items for processing
                        order_items.append({
                            "codigo": producto_id,
                            "nombre": descripcion,
                            "cantidad": cantidad
                        })
                        
                        has_products = True
                except (ValueError, TypeError):
                    continue
                    
        conn.commit()
        conn.close()
        
        if not has_products:
            return JSONResponse({"status": "error", "message": "No se seleccionaron productos"}, status_code=400)
        
        # Save PDF
        pdf_path = os.path.join(pdf_dir, f'orden_{orden_num}.pdf')
        print(f"Saving PDF to: {pdf_path}")
        pdf.output(pdf_path)
        print("PDF saved successfully")
        
        # Process the order
        try:
            print("Creating tables...")
            create_tables()
            print("Reading PDFs...")
            ordenes = leer_ordenes_de_pdfs()
            print(f"Found {len(ordenes)} orders")
            
            # We only need to process the current order
            orden = {
                "nro_orden": orden_num,
                "cliente": cliente,
                "fecha": current_date,
                "productos": order_items
            }
            print(f"Processing order: {orden}")
            orden_id = insertar_orden(orden)
            
            print("Updating stock...")
            actualizar_stock(venta_id)  # Pass the venta_id to only update products from this order
            print("Stock updated successfully")
            
            return JSONResponse({"status": "success", "order_number": orden_num})
            
        except Exception as e:
            print(f"Error processing order: {str(e)}")
            print(traceback.format_exc())
            # Don't raise here, return error response instead
            return JSONResponse(
                {"status": "error", "message": f"Error processing order: {str(e)}"},
                status_code=500
            )
            
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        print("Full traceback:")
        print(traceback.format_exc())
        return JSONResponse(
            {"status": "error", "message": f"Error al crear la orden: {str(e)}"},
            status_code=500
        )


@app.post("/bot_recepcion")
def run_recepcion():
    try:
        df = read_csv()
        if df is None:
            return {"status": "error", "message": "No se pudo leer el archivo CSV"}
        resultado = insert_or_update_products(df)
        print(f"[Bot Recepcion] Resultado: {resultado}")
        return {"status": "OK", "message": resultado}
    except Exception as e:
        print(f"Error in reception bot: {str(e)}")
        return JSONResponse(
            {"status": "error", "message": f"Error processing CSV: {str(e)}"},
            status_code=500
        )


@app.post("/bot_ventas")
async def run_ventas():
    try:
        print("Creating tables...")
        create_tables()
        print("Reading PDFs...")
        ordenes = leer_ordenes_de_pdfs()
        print(f"Found {len(ordenes)} orders")
        
        for orden in ordenes:
            print(f"Processing order: {orden}")
            insertar_orden(orden)
        
        print("Updating stock...")
        actualizar_stock()
        print("Stock updated successfully")
        
        return {"status": "OK", "message": "Órdenes cargadas y stock actualizado"}
    except Exception as e:
        print(f"Error in sales bot: {str(e)}")
        print(traceback.format_exc())
        return JSONResponse(
            {"status": "error", "message": f"Error processing orders: {str(e)}"},
            status_code=500
        )
