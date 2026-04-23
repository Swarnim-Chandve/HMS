from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models import UserRole
from app.repositories import user_repo, patient_repo
from app.schemas import RegisterPatientIn, RegisterReceptionistIn, TokenOut
from app.schemas.patient import PatientOut
from app.services.mappers import patient_to_out


def register_patient(db: Session, data: RegisterPatientIn) -> PatientOut:
    if user_repo.get_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
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


def register_receptionist(
    db: Session, data: RegisterReceptionistIn
) -> int:
    if user_repo.get_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    u = user_repo.create(
        db,
        email=str(data.email),
        full_name=data.full_name,
        password=data.password,
        role=UserRole.receptionist,
    )
    return u.id


def login(db: Session, email: str, password: str) -> TokenOut:
    user = user_repo.get_by_email(db, email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    token = create_access_token(
        str(user.id), extra={"role": user.role.value if hasattr(user.role, "value") else str(user.role)}
    )
    return TokenOut(access_token=token)
