from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.enums import AppointmentStatus
from app.schemas.common import ORMModel


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    reason: Optional[str] = None


class AppointmentUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    reason: Optional[str] = None


class AppointmentOut(ORMModel):
    id: int
    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    status: AppointmentStatus
    reason: Optional[str] = None
    created_by_user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
