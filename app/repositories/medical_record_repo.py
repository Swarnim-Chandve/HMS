from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import MedicalRecord, Patient
from app.models import MedicalRecord as MR


def get_by_id(db: Session, record_id: int) -> MedicalRecord | None:
    return db.scalars(
        select(MR)
        .options(
            joinedload(MR.patient).joinedload(Patient.user),
            joinedload(MR.doctor),
        )
        .where(MR.id == record_id)
    ).first()


def list_all(
    db: Session, *, skip: int = 0, limit: int = 100
) -> tuple[List[MedicalRecord], int]:
    total = int(db.scalar(select(func.count()).select_from(MR)) or 0)
    rows = db.scalars(
        select(MR).order_by(MR.id.desc()).offset(skip).limit(limit)
    ).all()
    return list(rows), total


def list_by_patient(
    db: Session, patient_id: int, *, skip: int = 0, limit: int = 50
) -> tuple[List[MedicalRecord], int]:
    q = select(MR).where(MR.patient_id == patient_id)
    total = int(
        db.scalar(
            select(func.count()).select_from(MR).where(MR.patient_id == patient_id)
        )
        or 0
    )
    rows = db.scalars(q.order_by(MR.recorded_at.desc()).offset(skip).limit(limit)).all()
    return list(rows), total


def create(
    db: Session,
    *,
    patient_id: int,
    doctor_id: int,
    appointment_id: int | None,
    diagnosis: str | None,
    notes: str | None,
    prescription: str | None,
) -> MR:
    r = MR(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_id=appointment_id,
        diagnosis=diagnosis,
        notes=notes,
        prescription=prescription,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def save(db: Session, r: MR) -> MR:
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def delete(db: Session, r: MR) -> None:
    db.delete(r)
    db.commit()
