from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import User, UserRole, InvoiceStatus
from app.repositories import billing_repo, patient_repo
from app.schemas.billing import InvoiceCreate, InvoiceOut, InvoiceStatusUpdate


def _to_out(inv) -> InvoiceOut:
    return InvoiceOut.model_validate(inv)


def list_invoices(
    db: Session,
    user: User,
    *,
    patient_id: int | None,
    skip: int,
    limit: int,
) -> tuple[list[InvoiceOut], int]:
    if user.role in (UserRole.admin, UserRole.receptionist):
        if patient_id is not None:
            rows, total = billing_repo.list_by_patient(
                db, patient_id, skip=skip, limit=limit
            )
        else:
            rows, total = billing_repo.list_all(db, skip=skip, limit=limit)
    elif user.role == UserRole.patient:
        p = patient_repo.get_by_user_id(db, user.id)
        if not p:
            return [], 0
        rows, total = billing_repo.list_by_patient(
            db, p.id, skip=skip, limit=limit
        )
    else:
        raise HTTPException(403, "Not allowed")
    return [_to_out(x) for x in rows], total


def get_invoice(db: Session, user: User, invoice_id: int) -> InvoiceOut:
    inv = billing_repo.get_by_id(db, invoice_id)
    if not inv:
        raise HTTPException(404, "Invoice not found")
    if user.role in (UserRole.admin, UserRole.receptionist):
        return _to_out(inv)
    if user.role == UserRole.patient:
        p = patient_repo.get_by_user_id(db, user.id)
        if p and inv.patient_id == p.id:
            return _to_out(inv)
    raise HTTPException(403, "Not allowed")


def create_invoice(
    db: Session, user: User, data: InvoiceCreate
) -> InvoiceOut:
    if user.role not in (UserRole.admin, UserRole.receptionist):
        raise HTTPException(403, "Not allowed")
    if not patient_repo.get_by_id(db, data.patient_id):
        raise HTTPException(400, "Invalid patient")
    lines: list[tuple[str, Decimal, Decimal]] = []
    for li in data.lines:
        q = li.quantity
        u = li.unit_price
        lines.append((li.description, q, u))
    inv = billing_repo.create_with_lines(
        db,
        patient_id=data.patient_id,
        appointment_id=data.appointment_id,
        due_date=data.due_date,
        description=data.description,
        lines=lines,
    )
    inv = billing_repo.get_by_id(db, inv.id)
    if not inv:
        raise HTTPException(500, "Create failed")
    return _to_out(inv)


def update_status(
    db: Session, user: User, invoice_id: int, data: InvoiceStatusUpdate
) -> InvoiceOut:
    if user.role not in (UserRole.admin, UserRole.receptionist):
        raise HTTPException(403, "Not allowed")
    inv = billing_repo.get_by_id(db, invoice_id)
    if not inv:
        raise HTTPException(404, "Invoice not found")
    inv.status = data.status
    if data.status == InvoiceStatus.paid:
        inv.paid_at = data.paid_at or datetime.now(timezone.utc)
    if data.paid_at is not None:
        inv.paid_at = data.paid_at
    inv = billing_repo.save(db, inv)
    return _to_out(inv)
