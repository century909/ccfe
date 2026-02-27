import psycopg2
import json
from uuid import uuid4

# Configuración de conexión (usando los datos del docker-compose)
DB_CONFIG = {
    "dbname": "ccfe_oraculo",
    "user": "diego",
    "password": "mia_secret_2026",
    "host": "localhost",
    "port": "5432"
}

PREVIEW_FILE = '/home/diego/Documentos/ccfe/migration_preview.json'

def create_tables(cursor):
    """Crea las tablas básicas en PostgreSQL"""
    print("🐘 Creando tablas en la base de datos...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            username TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS companies (
            id UUID PRIMARY KEY,
            ruc TEXT UNIQUE,
            name TEXT,
            address TEXT,
            timbrado TEXT
        );
        CREATE TABLE IF NOT EXISTS clients (
            id UUID PRIMARY KEY,
            company_id UUID REFERENCES companies(id),
            ruc TEXT,
            name TEXT,
            email TEXT
        );
        CREATE TABLE IF NOT EXISTS invoices (
            id UUID PRIMARY KEY,
            company_id UUID REFERENCES companies(id),
            client_id UUID REFERENCES clients(id),
            number TEXT,
            issue_date TIMESTAMP,
            total_amount NUMERIC(15, 2),
            status TEXT
        );
    """)

def load_data_to_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 1. Crear tablas
        create_tables(cur)
        
        # 2. Cargar datos del preview
        with open(PREVIEW_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print("📥 Insertando datos de prueba...")
        
        # Insertar Empresa
        c = data['company']
        cur.execute(
            "INSERT INTO companies (id, ruc, name, address, timbrado) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (ruc) DO NOTHING",
            (c['id'], c['ruc'], c['name'], c['address'], c['timbrado'])
        )
        
        # Insertar Clientes
        for cl in data['clients']:
            cur.execute(
                "INSERT INTO clients (id, company_id, ruc, name, email) VALUES (%s, %s, %s, %s, %s)",
                (cl['id'], cl['company_id'], cl['ruc'], cl['name'], cl['email'])
            )
            
        # Insertar Facturas
        for inv in data['invoices']:
            cur.execute(
                "INSERT INTO invoices (id, company_id, client_id, number, issue_date, total_amount, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (inv['id'], inv['company_id'], inv['client_id'], inv['number'], inv['issue_date'], inv['total_amount'], inv['status'])
            )
            
        conn.commit()
        print("✅ ¡Datos inyectados con éxito en PostgreSQL!")
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    load_data_to_db()
