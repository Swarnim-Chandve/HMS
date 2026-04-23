from decimal import Decimal
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Invoice, InvoiceLine, Patient
from app.models import Invoice as Inv


def get_by_id(db: Session, invoice_id: int) -> Invoice | None:
    return db.scalars(
        select(Inv)
        .options(
            joinedload(Inv.patient).joinedload(Patient.user),
            joinedload(Inv.lines),
        )
        .where(Inv.id == invoice_id)
    ).first()


def list_by_patient(
    db: Session, patient_id: int, *, skip: int = 0, limit: int = 50
) -> tuple[List[Invoice], int]:
    total = int(
        db.scalar(
            select(func.count())
            .select_from(Inv)
            .where(Inv.patient_id == patient_id)
        )
        or 0
    )
    rows = (
        db.scalars(
            select(Inv)
            .options(joinedload(Inv.lines))
            .where(Inv.patient_id == patient_id)
            .order_by(Inv.id.desc())
            .offset(skip)
            .limit(limit)
        )
        .unique()
        .all()
    )
    return list(rows), total


def list_all(
    db: Session, *, skip: int = 0, limit: int = 100
) -> tuple[List[Invoice], int]:
    total = int(db.scalar(select(func.count()).select_from(Inv)) or 0)
    rows = (
        db.scalars(
            select(Inv)
            .options(joinedload(Inv.lines), joinedload(Inv.patient).joinedload(Patient.user))
            .order_by(Inv.id.desc())
            .offset(skip)
            .limit(limit)
        )
        .unique()
        .all()
    )
    return list(rows), total


def create_with_lines(
    db: Session,
    *,
    patient_id: int,
    appointment_id: int | None,
    due_date,
    description: str | None,
    lines: list[tuple[str, Decimal, Decimal]],
) -> Inv:
    inv = Inv(
        patient_id=patient_id,
        appointment_id=appointment_id,
        due_date=due_date,
        description=description,
        amount_total=Decimal("0.00"),
    )
    total = Decimal("0.00")
    for desc, qty, unit in lines:
        line_total = (qty * unit).quantize(Decimal("0.01"))
        total += line_total
        inv.lines.append(
            InvoiceLine(
                description=desc,
                quantity=qty,
                unit_price=unit,
                line_total=line_total,
            )
        )
    inv.amount_total = total.quantize(Decimal("0.01"))
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


def save(db: Session, inv: Inv) -> Inv:
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv
