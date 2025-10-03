from fastapi import APIRouter, Depends, Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from .auth import get_current_user
from .models import Trip
from sqlmodel import Session, select
from .db import engine

router = APIRouter()

@router.get('/pdf')
def export_pdf(current_user=Depends(get_current_user)):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    y = 750
    with Session(engine) as session:
        statement = select(Trip).where(Trip.user_id == current_user.id)
        trips = session.exec(statement).all()
        p.setFont('Helvetica', 12)
        p.drawString(50, 800, f'Trip Report for user {current_user.email}')
        for t in trips:
            p.drawString(50, y, f"{t.id}: {t.destination} - {t.purpose} - ")
            y -= 20
            if y < 50:
                p.showPage()
                y = 750
    p.save()
    buffer.seek(0)
    return Response(content=buffer.read(), media_type='application/pdf')

@router.get('/chart')
def trips_chart(user=Depends(get_current_user)):
    with Session(engine) as session:
        statement = select(Trip).where(Trip.user_id == user.id)
        trips = session.exec(statement).all()
    counts = {}
    for t in trips:
        p = t.purpose or 'other'
        counts[p] = counts.get(p, 0) + 1
    return counts
