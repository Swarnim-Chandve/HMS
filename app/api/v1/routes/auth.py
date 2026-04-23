from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models import User, UserRole
from app.schemas import (
    LoginIn,
    MeOut,
    RegisterPatientIn,
    RegisterReceptionistIn,
    TokenOut,
)
from app.schemas.patient import PatientOut
from app.repositories import doctor_repo, patient_repo
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register/patient", response_model=PatientOut, status_code=status.HTTP_201_CREATED
)
def register_patient(
    data: RegisterPatientIn, db: Session = Depends(get_db)
) -> PatientOut:
    return auth_service.register_patient(db, data)


@router.post(
    "/register/receptionist", status_code=status.HTTP_201_CREATED
)
def register_receptionist(
    data: RegisterReceptionistIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
) -> dict:
    uid = auth_service.register_receptionist(db, data)
    return {"user_id": uid, "message": "Receptionist created"}


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    return auth_service.login(db, str(data.email), data.password)


@router.get("/me", response_model=MeOut)
def me(
    current: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> MeOut:
    pid: int | None = None
    did: int | None = None
    pr = patient_repo.get_by_user_id(db, current.id)
    if pr:
        pid = pr.id
    dr = doctor_repo.get_by_user_id(db, current.id)
    if dr:
        did = dr.id
    return MeOut(
        id=current.id,
        email=current.email,
        full_name=current.full_name,
        role=current.role,
        is_active=current.is_active,
        patient_id=pid,
        doctor_id=did,
    )
