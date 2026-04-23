from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import UserRole


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    # str (not EmailStr): internal/dev emails like *@hms.local are valid in DB but rejected by EmailStr
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1)


class MeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    patient_id: int | None = None
    doctor_id: int | None = None


class RegisterPatientIn(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=255)
    date_of_birth: date | None = None
    phone: str | None = None
    address: str | None = None
    emergency_contact: str | None = None


class RegisterReceptionistIn(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=255)
