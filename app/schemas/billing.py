from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import InvoiceStatus
from app.schemas.common import ORMModel


class InvoiceLineIn(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(default=Decimal("1"), ge=0)
    unit_price: Decimal = Field(ge=0)

    @field_validator("quantity", "unit_price", mode="before")
    @classmethod
    def to_decimal(cls, v: object) -> Decimal:
        if v is None:
            return Decimal("0")
        return Decimal(str(v))


class InvoiceCreate(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    due_date: Optional[date] = None
    description: Optional[str] = None
    lines: List[InvoiceLineIn] = Field(min_length=1)


class InvoiceStatusUpdate(BaseModel):
    status: InvoiceStatus
    paid_at: Optional[datetime] = None


class InvoiceLineOut(ORMModel):
    id: int
    invoice_id: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal


class InvoiceOut(ORMModel):
    id: int
    patient_id: int
    appointment_id: Optional[int] = None
    status: InvoiceStatus
    amount_total: Decimal
    due_date: Optional[date] = None
    paid_at: Optional[datetime] = None
    description: Optional[str] = None
    lines: List[InvoiceLineOut] = []
    created_at: datetime
    updated_at: datetime
