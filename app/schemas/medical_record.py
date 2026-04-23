from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class MedicalRecordCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    prescription: Optional[str] = None


class MedicalRecordUpdate(BaseModel):
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    prescription: Optional[str] = None
    appointment_id: Optional[int] = None


class MedicalRecordOut(ORMModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    diagnosis: Optional[str] = None
    notes: Optional[str] = None
    prescription: Optional[str] = None
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime
