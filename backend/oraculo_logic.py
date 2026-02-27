import os
import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database import Invoice, InvoiceItem, Client, Expense

# Configuración (Asegúrate de que coincida con database.py)
SQLALCHEMY_DATABASE_URL = "postgresql://diego:mia_secret_2026@localhost:5432/ccfe_oraculo"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class OraculoCCFE:
    def __init__(self, db_session):
        self.db = db_session

    def analizar_impuestos(self):
        """Analiza el IVA acumulado y proyectado (Débito vs Crédito)."""
        invoices = self.db.query(Invoice).all()
        expenses = self.db.query(Expense).all()
        
        total_venta = 0
        debito_iva = 0
        for inv in invoices:
            total_venta += float(inv.total_amount)
            debito_iva += (float(inv.total_amount) / 11)

        total_gastos = 0
        credito_iva = 0
        for exp in expenses:
            total_gastos += float(exp.total_amount)
            credito_iva += float(exp.vat_10) + float(exp.vat_5)

        neto_a_pagar = debito_iva - credito_iva

        return {
            "periodo": datetime.datetime.now().strftime("%B %Y"),
            "total_ventas_brutas": round(total_venta, 2),
            "debito_fiscal": round(debito_iva, 2),
            "total_gastos_brutos": round(total_gastos, 2),
            "credito_fiscal": round(credito_iva, 2),
            "iva_neto_estimado": round(neto_a_pagar, 2),
            "cantidad_facturas_emitidas": len(invoices),
            "cantidad_gastos_sincronizados": len(expenses)
        }

    def generar_sugerencia_fiscal(self, analisis):
        """Genera consejos basados en el balance real."""
        iva_neto = analisis["iva_neto_estimado"]
        if iva_neto > 0:
            return f"Sugerencia: Tienes un saldo a pagar de {iva_neto:,.0f} PYG. Gracias a CCFE-Sync hemos detectado {analisis['cantidad_gastos_sincronizados']} facturas de gastos que redujeron tu impuesto. ¡Sigue así!"
        else:
            return f"¡Excelente! Tienes un excedente de Crédito Fiscal de {abs(iva_neto):,.0f} PYG para este periodo. No tienes IVA a pagar por ahora."

if __name__ == "__main__":
    db = SessionLocal()
    oraculo = OraculoCCFE(db)
    res = oraculo.analizar_impuestos()
    print("--- REPORTE DEL ORÁCULO ---")
    print(f"Periodo: {res['periodo']}")
    print(f"Ventas Brutas: {res['total_ventas_brutas']:,} PYG")
    print(f"Débito Fiscal (IVA Ventas): {res['debito_fiscal']:,} PYG")
    print(f"Gastos Brutos (Sync): {res['total_gastos_brutos']:,} PYG")
    print(f"Facturas de Gastos Encontradas: {res['cantidad_gastos_sincronizados']}")
    print(f"Crédito Fiscal (IVA Compras): {res['credito_fiscal']:,} PYG")
    print("-" * 25)
    print(f"IVA NETO ESTIMADO: {res['iva_neto_estimado']:,} PYG")
    print("-" * 25)
    print(oraculo.generar_sugerencia_fiscal(res))
    db.close()
