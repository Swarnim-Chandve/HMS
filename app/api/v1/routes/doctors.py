from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.doctor import DoctorCreate, DoctorOut, DoctorUpdate
from app.services import doctor_service

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=dict)
def list_doctors(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    q: str | None = None,
) -> dict:
    items, total = doctor_service.list_doctors(
        db, user, skip=skip, limit=limit, q=q
    )
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DoctorOut:
    return doctor_service.get_doctor(db, user, doctor_id)


@router.post("", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
def create_doctor(
    data: DoctorCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DoctorOut:
    return doctor_service.create_doctor(db, user, data)


@router.patch("/{doctor_id}", response_model=DoctorOut)
def update_doctor(
    doctor_id: int,
    data: DoctorUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DoctorOut:
    return doctor_service.update_doctor(db, user, doctor_id, data)


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    doctor_service.delete_doctor(db, user, doctor_id)
    return None
