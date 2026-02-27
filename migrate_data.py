import csv
import json
import os
from uuid import uuid4
from datetime import datetime

# Rutas de archivos actuales
CLIENTS_CSV = '/home/diego/Documentos/ccfe/backend/clients.csv'
INVOICES_CSV = '/home/diego/Documentos/ccfe/backend/invoices.csv'
COMPANY_JSON = '/home/diego/Documentos/ccfe/company_profile.json'

# Salida para inspección antes de SQL
MIGRATION_JSON = '/home/diego/Documentos/ccfe/migration_preview.json'

def migrate():
    print("👾 Iniciando proceso de migración de datos...")
    
    # 1. Cargar Perfil de Empresa (Emisor)
    with open(COMPANY_JSON, 'r') as f:
        company_data = json.load(f)
    
    company_id = str(uuid4())
    company = {
        "id": company_id,
        "ruc": company_data['ruc'],
        "name": company_data['name'],
        "address": company_data['address'],
        "timbrado": company_data['timbrado']
    }

    # 2. Cargar Clientes
    clients = {}
    with open(CLIENTS_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            client_id = str(uuid4())
            clients[row['ruc']] = {
                "id": client_id,
                "company_id": company_id,
                "ruc": row['ruc'],
                "name": row['name'],
                "email": row['email']
            }

    # 3. Cargar Facturas
    invoices = []
    with open(INVOICES_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Vincular con el cliente si existe, sino crear uno genérico
            client = clients.get(row['client_ruc'])
            c_id = client['id'] if client else None
            
            invoices.append({
                "id": str(uuid4()),
                "company_id": company_id,
                "client_id": c_id,
                "number": row['invoice_number'],
                "issue_date": row['timestamp'],
                "total_amount": float(row['total_amount']),
                "status": row['sifen_status']
            })

    # 4. Guardar previsualización
    preview = {
        "company": company,
        "clients": list(clients.values()),
        "invoices": invoices
    }

    with open(MIGRATION_JSON, 'w', encoding='utf-8') as f:
        json.dump(preview, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Migración completada. Se procesaron {len(clients)} clientes y {len(invoices)} facturas.")
    print(f"📄 Revisa el archivo: {MIGRATION_JSON}")

if __name__ == "__main__":
    migrate()
