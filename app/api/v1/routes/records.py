from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordOut,
    MedicalRecordUpdate,
)
from app.services import medical_record_service

router = APIRouter(prefix="/medical-records", tags=["medical records"])


@router.get("", response_model=dict)
def list_records(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    patient_id: int | None = Query(default=None),
    skip: int = 0,
    limit: int = 50,
) -> dict:
    items, total = medical_record_service.list_records(
        db, user, patient_id=patient_id, skip=skip, limit=limit
    )
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{record_id}", response_model=MedicalRecordOut)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MedicalRecordOut:
    return medical_record_service.get_record(db, user, record_id)


@router.post(
    "", response_model=MedicalRecordOut, status_code=status.HTTP_201_CREATED
)
def create_record(
    data: MedicalRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MedicalRecordOut:
    return medical_record_service.create_record(db, user, data)


@router.patch("/{record_id}", response_model=MedicalRecordOut)
def update_record(
    record_id: int,
    data: MedicalRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MedicalRecordOut:
    return medical_record_service.update_record(db, user, record_id, data)


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    medical_record_service.delete_record(db, user, record_id)
    return None
