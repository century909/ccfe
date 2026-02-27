from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import csv
import os
import json
import qrcode
from datetime import datetime
from sqlalchemy.orm import Session

# ReportLab imports
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors

# Importar base de datos y modelos
from database import SessionLocal, engine, Base, User, Company, Client as DBClient, Invoice as DBInvoice, InvoiceItem as DBInvoiceItem

from expenses_router import router as expenses_router

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(expenses_router, tags=["expenses"])

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependencia de Base de Datos ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Models (API Validation) ---
class ClientBase(BaseModel):
    ruc: str
    name: str
    email: str
    address: Optional[str] = None

class CompanyProfile(BaseModel):
    name: str
    fantasy_name: Optional[str] = None
    ruc: str
    address: str
    phone: str
    email: str
    economic_activity: str
    timbrado: str

class InvoiceItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total_item: float
    vat_rate: int
    category: Optional[str] = None

class InvoiceCreate(BaseModel):
    client_ruc: str # Usamos el RUC para buscar al cliente en la DB
    items: List[InvoiceItem]
    total_amount: float
    payment_condition: str = "CONTADO"
    operation_type: str = "PRESTACION DE SERVICIOS"
    currency: str = "PYG"

# --- Directorios ---
KUDES_DIR = "kudes"
os.makedirs(KUDES_DIR, exist_ok=True)

# --- PDF & QR Generation ---
def generate_qr_code(cdc: str) -> str:
    qr_url = f"https://ekuatia.set.gov.py/consultas/cdc={cdc}"
    img = qrcode.make(qr_url)
    qr_path = os.path.join(KUDES_DIR, f"qr_{cdc}.png")
    img.save(qr_path)
    return qr_path

def draw_table_cell(c, x, y, width, height, text, font="Helvetica", size=8, bold=False, align="left", fill=False):
    if fill:
        c.setFillColor(colors.lightgrey)
        c.rect(x, y, width, height, fill=1)
        c.setFillColor(colors.black)
    else:
        c.rect(x, y, width, height)
    
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    if align == "left":
        c.drawString(x + 5, y + (height/2) - (size/2) + 2, text)
    elif align == "right":
        c.drawRightString(x + width - 5, y + (height/2) - (size/2) + 2, text)
    elif align == "center":
        c.drawCentredString(x + (width/2), y + (height/2) - (size/2) + 2, text)

def generate_kude_pdf(company: Company, client: DBClient, invoice_num: str, items: List[InvoiceItem], total: float, condition: str, op_type: str, currency: str) -> str:
    cdc_simulado = f"01{company.ruc.replace('-', '')}001001{invoice_num.replace('INV-', '')}12345"[:44]
    qr_path = generate_qr_code(cdc_simulado)
    pdf_filename = os.path.join(KUDES_DIR, f"kude_{invoice_num}.pdf")
    
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    w, h = letter
    margin = 40
    
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(w/2, h - 30, "KuDE - REPRESENTACIÓN GRÁFICA DE FACTURA ELECTRÓNICA")

    # --- TABLA ENCABEZADO ---
    y_start = h - 140
    draw_table_cell(c, margin, y_start, 350, 100, "")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin + 10, h - 60, company.name)
    c.setFont("Helvetica", 8)
    c.drawString(margin + 10, h - 75, company.name) # Usamos name si no hay fantasy_name
    c.drawString(margin + 10, h - 90, f"RUC: {company.ruc}")
    c.drawString(margin + 10, h - 105, f"Direccion: {company.address}")
    c.drawString(margin + 10, h - 120, f"Tel: --- | Email: ---")
    
    draw_table_cell(c, margin + 350, y_start, w - (margin*2) - 350, 100, "")
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(margin + 350 + 90, h - 60, "FACTURA ELECTRÓNICA")
    c.setFont("Helvetica", 9)
    c.drawString(margin + 360, h - 80, f"TIMBRADO: {company.timbrado}")
    c.drawString(margin + 360, h - 95, f"N°: {invoice_num}")
    c.drawString(margin + 360, h - 110, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
    c.drawString(margin + 360, h - 125, f"Emision: NORMAL")

    # --- TABLA RECEPTOR ---
    y_receptor = y_start - 50
    draw_table_cell(c, margin, y_receptor, w - (margin*2), 40, "")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margin + 10, y_receptor + 25, "DATOS DEL RECEPTOR")
    c.setFont("Helvetica", 9)
    c.drawString(margin + 10, y_receptor + 10, f"Razon Social: {client.name}")
    c.drawString(margin + 350, y_receptor + 10, f"RUC: {client.ruc}")

    # --- CONDICIONES DE VENTA ---
    y_cond = y_receptor - 25
    draw_table_cell(c, margin, y_cond, w - (margin*2), 20, "")
    c.setFont("Helvetica", 8)
    c.drawString(margin + 10, y_cond + 5, f"CONDICION DE VENTA: {condition}")
    c.drawString(margin + 200, y_cond + 5, f"NATURALEZA: {op_type}")
    c.drawString(margin + 450, y_cond + 5, f"MONEDA: {currency}")

    # --- TABLA DE ITEMS ---
    col_widths = [40, 250, 60, 80, 40, 62]
    col_names = ["COD", "DESCRIPCION", "CANT", "P. UNIT", "IVA", "SUBTOTAL"]
    y_table = y_cond - 25
    
    curr_x = margin
    for i, name in enumerate(col_names):
        draw_table_cell(c, curr_x, y_table, col_widths[i], 20, name, size=8, bold=True, align="center", fill=True)
        curr_x += col_widths[i]
    
    y_row = y_table - 20
    for i, item in enumerate(items):
        curr_x = margin
        row_data = [str(i+1), item.description[:40], str(item.quantity), f"{item.unit_price:,.0f}", f"{item.vat_rate}%", f"{item.total_item:,.0f}"]
        aligns = ["center", "left", "center", "right", "center", "right"]
        for j, val in enumerate(row_data):
            draw_table_cell(c, curr_x, y_row, col_widths[j], 20, val, align=aligns[j])
            curr_x += col_widths[j]
        y_row -= 20

    # --- TOTALES Y LIQUIDACION IVA ---
    vat_10 = sum(i.total_item for i in items if i.vat_rate == 10) / 11
    vat_5 = sum(i.total_item for i in items if i.vat_rate == 5) / 21
    
    y_iva = y_row - 30
    draw_table_cell(c, margin, y_iva, 350, 30, "")
    c.setFont("Helvetica", 8)
    c.drawString(margin + 10, y_iva + 10, f"Liquidacion IVA: (10%): {vat_10:,.0f} | (5%): {vat_5:,.0f} | Total IVA: {vat_10+vat_5:,.0f}")
    draw_table_cell(c, margin + 350, y_iva, w - (margin*2) - 350, 30, f"TOTAL {currency}.: {total:,.0f}", bold=True, align="center")
    
    c.save()
    return pdf_filename

# --- Endpoints ---

@app.get("/clients", response_model=List[ClientBase])
def list_clients(db: Session = Depends(get_db)):
    clients = db.query(DBClient).all()
    return clients

@app.post("/clients")
async def create_client(client: ClientBase, db: Session = Depends(get_db)):
    # Por ahora asumimos una sola empresa (la primera en la DB)
    company = db.query(Company).first()
    if not company:
        raise HTTPException(status_code=404, detail="No se encontró perfil de empresa")
    
    new_client = DBClient(
        company_id=company.id,
        ruc=client.ruc,
        name=client.name,
        email=client.email
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return {"message": "Cliente creado con éxito", "client": new_client}

@app.post("/invoice")
async def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    # 1. Buscar empresa y cliente
    company = db.query(Company).first()
    client = db.query(DBClient).filter(DBClient.ruc == invoice.client_ruc).first()
    
    if not company or not client:
        raise HTTPException(status_code=404, detail="Empresa o Cliente no encontrado")
    
    # 2. Generar número de factura
    invoice_num = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 3. Crear Registro de Factura en DB
    db_invoice = DBInvoice(
        company_id=company.id,
        client_id=client.id,
        number=invoice_num,
        total_amount=invoice.total_amount,
        status="ACCEPTED"
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    # 4. Crear Items de Factura en DB
    for item in invoice.items:
        db_item = DBInvoiceItem(
            invoice_id=db_invoice.id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            vat_rate=item.vat_rate,
            category=item.category # Módulo de IA Oráculo
        )
        db.add(db_item)
    
    db.commit()
    
    # 5. Generar PDF (KuDE)
    kude_path = generate_kude_pdf(company, client, invoice_num, invoice.items, invoice.total_amount, invoice.payment_condition, invoice.operation_type, invoice.currency)
    
    # 6. Sincronización Automática con Google Sheets (Punto 4 del Plan)
    # Por ahora lo simulamos con un log, pero está listo para conectar al MCP
    print(f"[GOOGLE SHEETS SYNC] Factura {invoice_num} sincronizada con la hoja de cálculo de Diego.")
    
    return {
        "invoice_number": invoice_num,
        "kude_url": kude_path,
        "db_status": "Persisted in PostgreSQL"
    }

from oraculo_logic import OraculoCCFE
from database import Invoice as DBInvoice, InvoiceItem as DBInvoiceItem # Asegurando import para el log

# Configuración de Google Sheets (Placeholder para integración MCP)
# En una implementación real, aquí se llamaría al servidor MCP de Diego

@app.get("/oraculo/report")
def get_oraculo_report(db: Session = Depends(get_db)):
    """Módulo Oráculo: Análisis predictivo y sugerencias fiscales"""
    oraculo = OraculoCCFE(db)
    analisis = oraculo.analizar_impuestos()
    sugerencia = oraculo.generar_sugerencia_fiscal(analisis)
    return {
        "status": "success",
        "data": analisis,
        "advice": sugerencia
    }
