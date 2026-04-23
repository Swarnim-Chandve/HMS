from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.repositories import patient_repo, user_repo
from app.schemas.patient import PatientCreate, PatientOut, PatientUpdate
from app.services.mappers import patient_to_out


def _check_patient_access(db: Session, user: User, patient_id: int) -> None:
    if user.role in (UserRole.admin, UserRole.receptionist, UserRole.doctor):
        return
    if user.role == UserRole.patient:
        row = patient_repo.get_by_user_id(db, user.id)
        if row and row.id == patient_id:
            return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")


def list_patients(
    db: Session,
    user: User,
    *,
    skip: int,
    limit: int,
    q: str | None,
) -> tuple[list[PatientOut], int]:
    if user.role not in (UserRole.admin, UserRole.receptionist, UserRole.doctor):
        raise HTTPException(403, "Not allowed")
    rows, total = patient_repo.list_(db, skip=skip, limit=limit, q=q)
    return [patient_to_out(p) for p in rows], total


def get_patient(db: Session, user: User, patient_id: int) -> PatientOut:
    _check_patient_access(db, user, patient_id)
    p = patient_repo.get_by_id(db, patient_id)
    if not p:
        raise HTTPException(404, "Patient not found")
    return patient_to_out(p)


def create_patient(
    db: Session, current: User, data: PatientCreate
) -> PatientOut:
    if current.role not in (UserRole.admin, UserRole.receptionist):
        raise HTTPException(403, "Not allowed")
    if user_repo.get_by_email(db, str(data.email)):
        raise HTTPException(409, "Email already registered")
    u = user_repo.create(
        db,
        email=str(data.email),
        full_name=data.full_name,
        password=data.password,
        role=UserRole.patient,
    )
    p = patient_repo.create_row(
        db,
        user_id=u.id,
        date_of_birth=data.date_of_birth,
        phone=data.phone,
        address=data.address,
        emergency_contact=data.emergency_contact,
    )
    p = patient_repo.get_by_id(db, p.id)
    if not p:
        raise HTTPException(500, "Failed to create patient")
    return patient_to_out(p)


def update_patient(
    db: Session, current: User, patient_id: int, data: PatientUpdate
) -> PatientOut:
    p = patient_repo.get_by_id(db, patient_id)
    if not p:
        raise HTTPException(404, "Patient not found")
    if current.role == UserRole.patient:
        row = patient_repo.get_by_user_id(db, current.id)
        if not row or row.id != patient_id:
            raise HTTPException(403, "Not allowed")
    elif current.role not in (UserRole.admin, UserRole.receptionist):
        raise HTTPException(403, "Not allowed")
    u = p.user
    if data.full_name is not None:
        u.full_name = data.full_name
        db.add(u)
    if data.date_of_birth is not None:
        p.date_of_birth = data.date_of_birth
    if data.phone is not None:
        p.phone = data.phone
    if data.address is not None:
        p.address = data.address
    if data.emergency_contact is not None:
        p.emergency_contact = data.emergency_contact
    p = patient_repo.update_row(db, p)
    p = patient_repo.get_by_id(db, p.id)
    if not p:
        raise HTTPException(500, "Update failed")
    return patient_to_out(p)


def delete_patient(db: Session, current: User, patient_id: int) -> None:
    if current.role != UserRole.admin:
        raise HTTPException(403, "Not allowed")
    p = patient_repo.get_by_id(db, patient_id)
    if not p:
        raise HTTPException(404, "Patient not found")
    u = user_repo.get_by_id(db, p.user_id)
    if u:
        user_repo.delete_user(db, u)
