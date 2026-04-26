"""
app/services/export_service.py
──────────────────────────────
Generación de reportes en Excel y PDF.
"""
import io
from datetime import datetime
import pandas as pd
from fpdf import FPDF
from sqlalchemy.orm import Session
from app.repositories.delivery_repository import delivery_repo
from app.schemas.delivery import DeliveryFilters

def generate_excel_report(db: Session, filters: DeliveryFilters) -> io.BytesIO:
    """Genera un archivo Excel con el listado de entregas filtrado."""
    # Desactivar paginación para exportar todo
    filters.size = 10000 
    data = delivery_repo.get_paginated(db, filters)
    deliveries = data["items"]

    # Preparar datos para DataFrame
    rows = []
    for d in deliveries:
        rows.append({
            "Tracking": d.tracking_no,
            "Estado": d.status,
            "Prioridad": d.priority,
            "Destinatario": d.recipient_name,
            "Teléfono": d.recipient_phone,
            "Dirección": f"{d.address.street}, {d.address.city}" if d.address else "N/A",
            "Programado": d.scheduled_at.strftime("%Y-%m-%d %H:%M") if d.scheduled_at else "N/A",
            "Repartidor": d.driver.full_name if d.driver else "Sin asignar",
            "Creado": d.created_at.strftime("%Y-%m-%d %H:%M")
        })

    df = pd.DataFrame(rows)
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Entregas')
        
    output.seek(0)
    return output

def generate_pdf_report(db: Session, filters: DeliveryFilters) -> bytes:
    """Genera un reporte PDF formal con el listado de entregas."""
    filters.size = 1000 
    data = delivery_repo.get_paginated(db, filters)
    deliveries = data["items"]

    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Header
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(30, 41, 59) # Slate 800
    pdf.cell(0, 10, 'Reporte de Gestión de Entregas - DMS Pro', ln=True, align='C')
    
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(100, 116, 139) # Slate 500
    pdf.cell(0, 10, f'Generado el: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')
    pdf.ln(5)

    # Table Header
    pdf.set_fill_color(59, 130, 246) # Blue 500
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 9)
    
    cols = [
        ("Tracking", 35), ("Estado", 30), ("Destinatario", 50), 
        ("Dirección", 70), ("Programado", 40), ("Prioridad", 20)
    ]
    
    for col_name, width in cols:
        pdf.cell(width, 10, col_name, border=1, align='C', fill=True)
    pdf.ln()

    # Table Rows
    pdf.set_fill_color(248, 250, 252)
    pdf.set_text_color(51, 65, 85)
    pdf.set_font('Arial', '', 8)
    
    fill = False
    for d in deliveries:
        pdf.cell(35, 8, str(d.tracking_no), border=1, fill=fill)
        pdf.cell(30, 8, str(d.status), border=1, fill=fill)
        pdf.cell(50, 8, str(d.recipient_name)[:25], border=1, fill=fill)
        pdf.cell(70, 8, f"{d.address.street[:35]}..." if d.address else "N/A", border=1, fill=fill)
        pdf.cell(40, 8, d.scheduled_at.strftime("%Y-%m-%d %H:%M"), border=1, fill=fill)
        pdf.cell(20, 8, str(d.priority), border=1, align='C', fill=fill)
        pdf.ln()
        fill = not fill

    return pdf.output(dest='S')
