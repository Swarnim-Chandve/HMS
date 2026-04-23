from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Doctor, User


def get_by_id(db: Session, doctor_id: int) -> Doctor | None:
    return db.scalars(
        select(Doctor)
        .options(joinedload(Doctor.user))
        .where(Doctor.id == doctor_id)
    ).first()


def get_by_user_id(db: Session, user_id: int) -> Doctor | None:
    return db.scalars(
        select(Doctor)
        .options(joinedload(Doctor.user))
        .where(Doctor.user_id == user_id)
    ).first()


def list_(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 50,
    q: str | None = None,
) -> tuple[list[Doctor], int]:
    count_q = select(func.count(Doctor.id)).select_from(Doctor).join(
        User, Doctor.user_id == User.id
    )
    data_q = (
        select(Doctor)
        .options(joinedload(Doctor.user))
        .join(User, Doctor.user_id == User.id)
    )
    if q:
        t = f"%{q}%"
        filt = or_(User.email.ilike(t), User.full_name.ilike(t))
        count_q = count_q.where(filt)
        data_q = data_q.where(filt)
    total = int(db.scalar(count_q) or 0)
    rows = (
        db.scalars(
            data_q.order_by(Doctor.id.desc()).offset(skip).limit(limit)
        )
        .unique()
        .all()
    )
    return list(rows), total


def create_row(
    db: Session,
    *,
    user_id: int,
    specialization: str | None,
    license_number: str | None,
    department: str | None,
) -> Doctor:
    d = Doctor(
        user_id=user_id,
        specialization=specialization,
        license_number=license_number,
        department=department,
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def update_row(db: Session, d: Doctor) -> Doctor:
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def delete_row(db: Session, d: Doctor) -> None:
    db.delete(d)
    db.commit()
