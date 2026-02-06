from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import csv
import os
import json
from datetime import datetime

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib import colors

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class Client(BaseModel):
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
    vat_rate: int # 0 for exempt, 5 for 5%, 10 for 10%

class Invoice(BaseModel):
    client: Client
    items: List[InvoiceItem]
    total_amount: float
    invoice_number: Optional[str] = None

# --- JSON File Handling for Company Profile ---
COMPANY_PROFILE_FILE = "company_profile.json"

def save_company_profile(profile: CompanyProfile):
    with open(COMPANY_PROFILE_FILE, 'w', encoding='utf-8') as f:
        json.dump(profile.dict(), f, indent=4)

def load_company_profile() -> Optional[CompanyProfile]:
    if not os.path.exists(COMPANY_PROFILE_FILE):
        return None
    with open(COMPANY_PROFILE_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            return CompanyProfile(**data)
        except (json.JSONDecodeError, TypeError):
            return None

# --- CSV Handling for Invoices ---
INVOICES_CSV_FILE = "invoices.csv"
INVOICES_CSV_HEADERS = ["timestamp", "invoice_number", "client_ruc", "client_name", "client_email", "total_amount", "sifen_status", "kude_url", "email_sent"]

def initialize_invoices_csv():
    if not os.path.exists(INVOICES_CSV_FILE):
        with open(INVOICES_CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(INVOICES_CSV_HEADERS)

def append_invoice_to_csv(invoice_data: dict):
    initialize_invoices_csv()
    with open(INVOICES_CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            invoice_data.get("timestamp"),
            invoice_data.get("invoice_number"),
            invoice_data.get("client_ruc"),
            invoice_data.get("client_name"),
            invoice_data.get("client_email"),
            invoice_data.get("total_amount"),
            invoice_data.get("sifen_status"),
            invoice_data.get("kude_url"),
            invoice_data.get("email_sent")
        ])

# --- CSV Handling for Clients ---
CLIENTS_CSV_FILE = "clients.csv"
CLIENTS_CSV_HEADERS = ["ruc", "name", "email", "address"]

def initialize_clients_csv():
    if not os.path.exists(CLIENTS_CSV_FILE):
        with open(CLIENTS_CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(CLIENTS_CSV_HEADERS)

def append_client_to_csv(client: Client):
    initialize_clients_csv()
    with open(CLIENTS_CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([client.ruc, client.name, client.email, client.address])

def get_all_clients() -> List[Client]:
    initialize_clients_csv()
    clients = []
    with open(CLIENTS_CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            clients.append(Client(**row))
    return clients

# --- KUDE & SIFEN Functions ---
def generate_sifen_xml(invoice: Invoice) -> str:
    print(f"Simulating SIFEN XML generation for invoice: {invoice.invoice_number}")
    return f"<sifen_xml>Invoice {invoice.invoice_number} data...</sifen_xml>"

KUDES_DIR = "kudes"
os.makedirs(KUDES_DIR, exist_ok=True)

def generate_kude_pdf(invoice: Invoice) -> str:
    """Generates a mock KUDE (PDF) for the invoice, using company profile data."""
    print("Generating mock KUDE (PDF).")
    
    profile = load_company_profile()
    # Default/Placeholder company data if not set
    default_profile = CompanyProfile(
        name="Mi Empresa S.A.",
        fantasy_name="Mi Empresa",
        ruc="80000000-1",
        address="Av. Principal 123, Asunción",
        phone="021 123456",
        email="info@miempresa.com.py",
        economic_activity="Venta de Productos Varios",
        timbrado="12345678"
    )
    company_data = profile if profile else default_profile

    pdf_filename = os.path.join(KUDES_DIR, f"kude_{invoice.invoice_number}.pdf")
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Modify existing styles and add new ones
    styles['Normal'].fontSize = 10
    styles['Normal'].fontName = 'Helvetica'
    
    styles.add(ParagraphStyle(name='Small', fontSize=8, fontName='Helvetica'))
    styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='BoldHeader', fontSize=12, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='InvoiceTitle', fontSize=18, fontName='Helvetica-Bold', alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='KudeHeader', fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER))

    story = []

    # --- KUDE Header ---
    story.append(Paragraph("KuDE de FACTURA ELECTRÓNICA", styles['KudeHeader']))
    story.append(Spacer(1, 0.1 * inch))

    # --- Header Table (Company Info vs Invoice Details) ---
    header_data = [
        [
            Paragraph(f"<b>{company_data.name}</b>", styles['Normal']),
            Paragraph("Timbrado N°: " + company_data.timbrado, styles['Small'])
        ],
        [
            Paragraph(f"RUC: {company_data.ruc}", styles['Normal']),
            Paragraph("RUC: " + company_data.ruc, styles['Small'])
        ],
        [
            Paragraph(company_data.address, styles['Normal']),
            Paragraph("Fecha de Inicio de Vigencia: " + datetime.now().strftime('%d/%m/%Y'), styles['Small'])
        ],
        [
            Paragraph(f"Teléfono: {company_data.phone}", styles['Normal']),
            ""
        ],
        [
            Paragraph(f"Email: {company_data.email}", styles['Normal']),
            ""
        ],
        [
            Paragraph(f"Actividad Económica: {company_data.economic_activity}", styles['Normal']),
            ""
        ],
        [
            "",
            Paragraph(f"<b>FACTURA ELECTRÓNICA</b>", styles['InvoiceTitle'])
        ],
        [
            "",
            Paragraph(f"<b>{invoice.invoice_number}</b>", styles['InvoiceTitle'])
        ]
    ]
    header_table = Table(header_data, colWidths=[4.0 * inch, 3.0 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,5), 'RIGHT'),
        ('ALIGN', (1,6), (1,7), 'RIGHT'),
        ('SPAN', (1,6), (1,7)),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.2 * inch))

    # --- Client Details ---
    story.append(Paragraph("<b>Datos del Cliente:</b>", styles['BoldHeader']))
    client_details = [
        [Paragraph("Nombre/Razón Social:", styles['Normal']), Paragraph(invoice.client.name, styles['Normal'])],
        [Paragraph("RUC/Documento N°:", styles['Normal']), Paragraph(invoice.client.ruc, styles['Normal'])],
        [Paragraph("Dirección:", styles['Normal']), Paragraph(invoice.client.address or "N/A", styles['Normal'])],
        [Paragraph("Correo Electrónico:", styles['Normal']), Paragraph(invoice.client.email, styles['Normal'])],
    ]
    client_table = Table(client_details, colWidths=[2.0 * inch, 5.0 * inch])
    client_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 0.2 * inch))

    # --- Invoice Items Table ---
    story.append(Paragraph("<b>Detalle de Ítems:</b>", styles['BoldHeader']))
    item_data = [
        [
            Paragraph("<b>Descripción</b>", styles['Small']),
            Paragraph("<b>Cantidad</b>", styles['Small']),
            Paragraph("<b>P. Unitario</b>", styles['Small']),
            Paragraph("<b>IVA</b>", styles['Small']),
            Paragraph("<b>Total</b>", styles['Small'])
        ]
    ]
    for item in invoice.items:
        item_data.append([
            Paragraph(item.description, styles['Small']),
            Paragraph(str(item.quantity), styles['Small']),
            Paragraph(f"{item.unit_price:.2f}", styles['Small']),
            Paragraph(f"{item.vat_rate}%", styles['Small']),
            Paragraph(f"{item.total_item:.2f}", styles['Small'])
        ])
    
    item_table = Table(item_data, colWidths=[3.0 * inch, 0.8 * inch, 1.2 * inch, 0.5 * inch, 1.5 * inch])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.25, colors.black),
    ]))
    story.append(item_table)
    story.append(Spacer(1, 0.2 * inch))

    # --- Totals and VAT Summary ---
    total_data = [
        [Paragraph("<b>SUBTOTAL:</b>", styles['Normal']), Paragraph(f"{invoice.total_amount:.2f}", styles['Normal'])],
        [Paragraph("<b>TOTAL DE LA OPERACIÓN:</b>", styles['Normal']), Paragraph(f"{invoice.total_amount:.2f}", styles['Normal'])],
        [Paragraph("<b>TOTAL EN GUARANIES:</b>", styles['Normal']), Paragraph(f"{invoice.total_amount:.2f}", styles['Normal'])],
    ]
    total_table = Table(total_data, colWidths=[5.0 * inch, 2.0 * inch])
    total_table.setStyle(TableStyle([
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 0.1 * inch))

    # Detailed VAT calculation
    vat_10_base = sum(item.total_item for item in invoice.items if item.vat_rate == 10)
    vat_5_base = sum(item.total_item for item in invoice.items if item.vat_rate == 5)
    exempt_total = sum(item.total_item for item in invoice.items if item.vat_rate == 0)
    
    vat_10_amount = vat_10_base / 11
    vat_5_amount = vat_5_base / 21
    total_vat = vat_10_amount + vat_5_amount

    vat_summary_data = [
        [
            Paragraph("<b>LIQUIDACIÓN IVA:</b>", styles['Normal']),
            Paragraph(f"(5%) {vat_5_amount:.2f}", styles['Normal']),
            Paragraph(f"(10%) {vat_10_amount:.2f}", styles['Normal']),
            Paragraph("<b>TOTAL IVA:</b>", styles['Normal']),
            Paragraph(f"{total_vat:.2f}", styles['Normal'])
        ]
    ]
    vat_table = Table(vat_summary_data, colWidths=[2.5 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch, 1.5 * inch])
    vat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.25, colors.black),
    ]))
    story.append(vat_table)
    story.append(Spacer(1, 0.4 * inch))

    # --- QR Code and CDC Placeholder ---
    story.append(Paragraph("Consulte la validez de esta Factura Electrónica con el número CDC impreso abajo en:", styles['Small']))
    story.append(Paragraph("https://ekuatia.set.gov.py/consultas/", styles['Small']))
    story.append(Spacer(1, 0.1 * inch))
    
    story.append(Paragraph("<b>[QR CODE PLACEHOLDER]</b>", styles['Center']))
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph("<b>CDC: [CÓDIGO DE CONTROL SIFEN SIMULADO]</b>", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # --- Legal Disclaimer ---
    legal_text = "ESTE DOCUMENTO ES UNA REPRESENTACIÓN GRÁFICA DEL DOCUMENTO ELECTRÓNICO (XML). Si su documento electrónico presenta algún error, podrá solicitar la modificación dentro de las 72 horas siguientes de la emisión de este comprobante."
    story.append(Paragraph(legal_text, styles['Small']))
    story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    return pdf_filename

def send_invoice_email(client_email: str, kude_path: str, invoice_number: str):
    print(f"Simulating email sent to {client_email} for invoice {invoice_number}.")
    print(f"Attached KUDE PDF: {kude_path}")
    pass

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Electronic Invoicing API for Paraguay!"}

@app.post("/company-profile")
async def create_or_update_company_profile(profile: CompanyProfile):
    save_company_profile(profile)
    return {"message": "Company profile saved successfully.", "profile": profile}

@app.get("/company-profile", response_model=Optional[CompanyProfile])
async def get_company_profile():
    return load_company_profile()

@app.post("/clients")
async def create_client(client: Client):
    all_clients = get_all_clients()
    if any(c.ruc == client.ruc for c in all_clients):
        raise HTTPException(status_code=400, detail="Client with this RUC already exists.")
    append_client_to_csv(client)
    return {"message": "Client created successfully.", "client": client}

@app.get("/clients", response_model=List[Client])
async def list_clients():
    return get_all_clients()

@app.post("/invoice")
async def create_invoice(invoice: Invoice):
    invoice.invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    kude_path = generate_kude_pdf(invoice)
    send_invoice_email(invoice.client.email, kude_path, invoice.invoice_number)
    
    invoice_data_to_log = {
        "timestamp": datetime.now().isoformat(),
        "invoice_number": invoice.invoice_number,
        "client_ruc": invoice.client.ruc,
        "client_name": invoice.client.name,
        "client_email": invoice.client.email,
        "total_amount": invoice.total_amount,
        "sifen_status": "SIMULATED_ACCEPTED",
        "kude_url": kude_path,
        "email_sent": True
    }
    append_invoice_to_csv(invoice_data_to_log)

    return {
        "message": "Invoice created and processed successfully (simulated).",
        "invoice_number": invoice.invoice_number,
        "kude_url": kude_path,
    }
