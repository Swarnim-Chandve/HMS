from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentUpdate
from app.services import appointment_service

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("", response_model=dict)
def list_appointments(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> dict:
    items, total = appointment_service.list_appointments(
        db, user, skip=skip, limit=limit
    )
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AppointmentOut:
    return appointment_service.get_appointment(db, user, appointment_id)


@router.post(
    "", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED
)
def create_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AppointmentOut:
    return appointment_service.create_appointment(db, user, data)


@router.patch("/{appointment_id}", response_model=AppointmentOut)
def update_appointment(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AppointmentOut:
    return appointment_service.update_appointment(
        db, user, appointment_id, data
    )


@router.delete(
    "/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(
        get_current_user
    ),  # admin/receptionist only in service
) -> None:
    appointment_service.delete_appointment(db, user, appointment_id)
    return None
