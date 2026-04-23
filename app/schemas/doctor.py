from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class DoctorCreate(BaseModel):
    # str: allows dev domains like *.test.local without EmailStr blocking
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=255)
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    department: Optional[str] = None


class DoctorUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    department: Optional[str] = None


class DoctorOut(ORMModel):
    id: int
    user_id: int
    email: str
    full_name: str
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    department: Optional[str] = None
    created_at: datetime
    updated_at: datetime
