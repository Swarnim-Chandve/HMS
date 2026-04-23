from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Patient, User


def get_by_id(db: Session, patient_id: int) -> Patient | None:
    return db.scalars(
        select(Patient)
        .options(joinedload(Patient.user))
        .where(Patient.id == patient_id)
    ).first()


def get_by_user_id(db: Session, user_id: int) -> Patient | None:
    return db.scalars(
        select(Patient)
        .options(joinedload(Patient.user))
        .where(Patient.user_id == user_id)
    ).first()


def list_(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    q: str | None = None,
) -> tuple[list[Patient], int]:
    count_q = select(func.count(Patient.id)).select_from(Patient).join(
        User, Patient.user_id == User.id
    )
    data_q = (
        select(Patient)
        .options(joinedload(Patient.user))
        .join(User, Patient.user_id == User.id)
    )
    if q:
        t = f"%{q}%"
        filt = or_(User.email.ilike(t), User.full_name.ilike(t))
        count_q = count_q.where(filt)
        data_q = data_q.where(filt)
    total = int(db.scalar(count_q) or 0)
    rows = (
        db.scalars(
            data_q.order_by(Patient.id.desc()).offset(skip).limit(limit)
        )
        .unique()
        .all()
    )
    return list(rows), total


def create_row(
    db: Session,
    *,
    user_id: int,
    date_of_birth,
    phone: str | None,
    address: str | None,
    emergency_contact: str | None,
) -> Patient:
    p = Patient(
        user_id=user_id,
        date_of_birth=date_of_birth,
        phone=phone,
        address=address,
        emergency_contact=emergency_contact,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def update_row(db: Session, p: Patient) -> Patient:
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def delete_row(db: Session, p: Patient) -> None:
    db.delete(p)
    db.commit()
