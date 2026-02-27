from sqlalchemy import create_engine, Column, String, Float, DateTime, ForeignKey, Numeric, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime

# Configuración de la conexión
# Cambia 'mia_secret_2026' si decidiste usar otra contraseña
SQLALCHEMY_DATABASE_URL = "postgresql://diego:mia_secret_2026@localhost:5432/ccfe_oraculo"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- Modelos SQLAlchemy ---

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Company(Base):
    __tablename__ = "companies"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ruc = Column(String, unique=True, index=True)
    name = Column(String)
    address = Column(String)
    timbrado = Column(String)
    
    clients = relationship("Client", back_populates="company")
    invoices = relationship("Invoice", back_populates="company")

class Client(Base):
    __tablename__ = "clients"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    ruc = Column(String, index=True)
    name = Column(String)
    email = Column(String)
    
    company = relationship("Company", back_populates="clients")
    invoices = relationship("Invoice", back_populates="client")

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    number = Column(String, unique=True, index=True)
    issue_date = Column(DateTime, default=datetime.datetime.utcnow)
    total_amount = Column(Numeric(15, 2))
    status = Column(String)
    
    company = relationship("Company", back_populates="invoices")
    client = relationship("Client", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"))
    description = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Numeric(15, 2))
    vat_rate = Column(Integer) # 0, 5, 10
    category = Column(String, nullable=True) # El campo clave para la IA
    
    invoice = relationship("Invoice", back_populates="items")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    number = Column(String, index=True) # Número de factura del proveedor
    issue_date = Column(DateTime)
    ruc_supplier = Column(String, index=True)
    name_supplier = Column(String)
    total_amount = Column(Numeric(15, 2))
    vat_10 = Column(Numeric(15, 2), default=0)
    vat_5 = Column(Numeric(15, 2), default=0)
    exempt = Column(Numeric(15, 2), default=0)
    timbrado = Column(String)
    xml_filename = Column(String, nullable=True) # Referencia al archivo original
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    company = relationship("Company", back_populates="expenses")

# Actualizar el modelo Company para incluir la relación
Company.expenses = relationship("Expense", back_populates="company")
