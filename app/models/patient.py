from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.appointment import Appointment
    from app.models.medical_record import MedicalRecord
    from app.models.billing import Invoice


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    emergency_contact: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    user: Mapped["User"] = relationship("User", back_populates="patient")
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment", back_populates="patient"
    )
    medical_records: Mapped[List["MedicalRecord"]] = relationship(
        "MedicalRecord", back_populates="patient"
    )
    invoices: Mapped[List["Invoice"]] = relationship(
        "Invoice", back_populates="patient"
    )
