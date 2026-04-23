from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.repositories import doctor_repo, user_repo
from app.schemas.doctor import DoctorCreate, DoctorOut, DoctorUpdate
from app.services.mappers import doctor_to_out


def list_doctors(
    db: Session, user: User, *, skip: int, limit: int, q: str | None
) -> tuple[list[DoctorOut], int]:
    if user.role not in (
        UserRole.admin,
        UserRole.receptionist,
        UserRole.patient,
        UserRole.doctor,
    ):
        raise HTTPException(403, "Not allowed")
    rows, total = doctor_repo.list_(db, skip=skip, limit=limit, q=q)
    return [doctor_to_out(d) for d in rows], total


def get_doctor(db: Session, user: User, doctor_id: int) -> DoctorOut:
    if user.role not in (
        UserRole.admin,
        UserRole.receptionist,
        UserRole.patient,
        UserRole.doctor,
    ):
        raise HTTPException(403, "Not allowed")
    d = doctor_repo.get_by_id(db, doctor_id)
    if not d:
        raise HTTPException(404, "Doctor not found")
    return doctor_to_out(d)


def create_doctor(db: Session, current: User, data: DoctorCreate) -> DoctorOut:
    if current.role != UserRole.admin:
        raise HTTPException(403, "Only admin can create doctors")
    if user_repo.get_by_email(db, str(data.email)):
        raise HTTPException(409, "Email already registered")
    u = user_repo.create(
        db,
        email=str(data.email),
        full_name=data.full_name,
        password=data.password,
        role=UserRole.doctor,
    )
    d = doctor_repo.create_row(
        db,
        user_id=u.id,
        specialization=data.specialization,
        license_number=data.license_number,
        department=data.department,
    )
    d2 = doctor_repo.get_by_id(db, d.id)
    if not d2:
        raise HTTPException(500, "Failed to create doctor")
    return doctor_to_out(d2)


def update_doctor(
    db: Session, current: User, doctor_id: int, data: DoctorUpdate
) -> DoctorOut:
    d = doctor_repo.get_by_id(db, doctor_id)
    if not d:
        raise HTTPException(404, "Doctor not found")
    u = d.user
    if current.role == UserRole.doctor:
        if current.id != d.user_id:
            raise HTTPException(403, "Not allowed")
    elif current.role != UserRole.admin:
        raise HTTPException(403, "Not allowed")
    if data.full_name is not None:
        u.full_name = data.full_name
        db.add(u)
    if data.specialization is not None:
        d.specialization = data.specialization
    if data.license_number is not None:
        d.license_number = data.license_number
    if data.department is not None:
        d.department = data.department
    d = doctor_repo.update_row(db, d)
    d2 = doctor_repo.get_by_id(db, d.id)
    if not d2:
        raise HTTPException(500, "Update failed")
    return doctor_to_out(d2)


def delete_doctor(db: Session, current: User, doctor_id: int) -> None:
    if current.role != UserRole.admin:
        raise HTTPException(403, "Not allowed")
    d = doctor_repo.get_by_id(db, doctor_id)
    if not d:
        raise HTTPException(404, "Doctor not found")
    u = user_repo.get_by_id(db, d.user_id)
    if u:
        user_repo.delete_user(db, u)
