from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.patient import PatientCreate, PatientOut, PatientUpdate
from app.services import patient_service

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=dict)
def list_patients(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    q: str | None = None,
) -> dict:
    items, total = patient_service.list_patients(
        db, user, skip=skip, limit=limit, q=q
    )
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PatientOut:
    return patient_service.get_patient(db, user, patient_id)


@router.post(
    "", response_model=PatientOut, status_code=status.HTTP_201_CREATED
)
def create_patient(
    data: PatientCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PatientOut:
    return patient_service.create_patient(db, user, data)


@router.patch("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: int,
    data: PatientUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PatientOut:
    return patient_service.update_patient(db, user, patient_id, data)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    patient_service.delete_patient(db, user, patient_id)
    return None
