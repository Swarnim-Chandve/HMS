from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.appointment import Appointment
    from app.models.medical_record import MedicalRecord


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    specialization: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    license_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    user: Mapped["User"] = relationship("User", back_populates="doctor")
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment", back_populates="doctor"
    )
    medical_records: Mapped[List["MedicalRecord"]] = relationship(
        "MedicalRecord", back_populates="doctor"
    )
