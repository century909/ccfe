from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import SessionLocal, Expense, Company
import xml.etree.ElementTree as ET
import base64

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ExpenseCreate(BaseModel):
    number: str
    issue_date: datetime
    ruc_supplier: str
    name_supplier: str
    total_amount: float
    vat_10: float = 0
    vat_5: float = 0
    exempt: float = 0
    timbrado: str
    xml_filename: Optional[str] = None

@router.post("/expenses")
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    company = db.query(Company).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no configurada")
    
    # Evitar duplicados por número de factura y RUC del proveedor
    existing = db.query(Expense).filter(
        Expense.number == expense.number,
        Expense.ruc_supplier == expense.ruc_supplier
    ).first()
    
    if existing:
        return {"message": "Gasto ya registrado", "id": existing.id}

    db_expense = Expense(
        company_id=company.id,
        number=expense.number,
        issue_date=expense.issue_date,
        ruc_supplier=expense.ruc_supplier,
        name_supplier=expense.name_supplier,
        total_amount=expense.total_amount,
        vat_10=expense.vat_10,
        vat_5=expense.vat_5,
        exempt=expense.exempt,
        timbrado=expense.timbrado,
        xml_filename=expense.xml_filename
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.get("/expenses", response_model=List[ExpenseCreate])
def list_expenses(db: Session = Depends(get_db)):
    return db.query(Expense).all()
