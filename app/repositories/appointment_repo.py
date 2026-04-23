from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Appointment, AppointmentStatus, Doctor, Patient
from app.models import Appointment as A


def get_by_id(db: Session, appt_id: int) -> Appointment | None:
    return db.scalars(
        select(A)
        .options(
            joinedload(A.patient).joinedload(Patient.user),
            joinedload(A.doctor).joinedload(Doctor.user),
        )
        .where(A.id == appt_id)
    ).first()


def _apply_scope(
    stmt,
    *,
    patient_id: int | None,
    doctor_id: int | None,
):
    if patient_id is not None:
        stmt = stmt.where(A.patient_id == patient_id)
    if doctor_id is not None:
        stmt = stmt.where(A.doctor_id == doctor_id)
    return stmt


def list_for_user_scope(
    db: Session,
    *,
    patient_id: int | None = None,
    doctor_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[Appointment], int]:
    base = select(A).options(
        joinedload(A.patient).joinedload(Patient.user),
        joinedload(A.doctor).joinedload(Doctor.user),
    )
    base = _apply_scope(base, patient_id=patient_id, doctor_id=doctor_id)
    count_q = select(func.count()).select_from(A)
    count_q = _apply_scope(count_q, patient_id=patient_id, doctor_id=doctor_id)
    total = int(db.scalar(count_q) or 0)
    rows = (
        db.scalars(
            base.order_by(A.scheduled_at.desc()).offset(skip).limit(limit)
        )
        .unique()
        .all()
    )
    return list(rows), total


def list_all(
    db: Session, *, skip: int = 0, limit: int = 100
) -> tuple[List[Appointment], int]:
    return list_for_user_scope(
        db, patient_id=None, doctor_id=None, skip=skip, limit=limit
    )


def conflicting_window(
    db: Session,
    *,
    doctor_id: int,
    scheduled_at: datetime,
    exclude_appointment_id: int | None = None,
) -> bool:
    if scheduled_at.tzinfo is None:
        scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)
    start = scheduled_at - timedelta(minutes=30)
    end = scheduled_at + timedelta(minutes=30)
    stmt = select(A).where(
        A.doctor_id == doctor_id,
        A.status != AppointmentStatus.cancelled,
        A.scheduled_at >= start,
        A.scheduled_at <= end,
    )
    if exclude_appointment_id is not None:
        stmt = stmt.where(A.id != exclude_appointment_id)
    return db.scalars(stmt).first() is not None


def create(
    db: Session,
    *,
    patient_id: int,
    doctor_id: int,
    scheduled_at: datetime,
    reason: str | None,
    created_by_user_id: int | None,
) -> A:
    ap = A(
        patient_id=patient_id,
        doctor_id=doctor_id,
        scheduled_at=scheduled_at,
        reason=reason,
        status=AppointmentStatus.scheduled,
        created_by_user_id=created_by_user_id,
    )
    db.add(ap)
    db.commit()
    db.refresh(ap)
    return ap


def save(db: Session, ap: A) -> A:
    db.add(ap)
    db.commit()
    db.refresh(ap)
    return ap


def delete(db: Session, ap: A) -> None:
    db.delete(ap)
    db.commit()
