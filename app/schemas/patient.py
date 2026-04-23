from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class PatientBase(BaseModel):
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None


class PatientCreate(PatientBase):
    # When admin/receptionist creates, they supply user account fields
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=255)


class PatientUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)


class PatientOut(ORMModel):
    id: int
    user_id: int
    email: str
    full_name: str
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    created_at: datetime
    updated_at: datetime
