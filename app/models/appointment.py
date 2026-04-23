from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import DateTime, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AppointmentStatus

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.doctor import Doctor
    from app.models.user import User
    from app.models.medical_record import MedicalRecord
    from app.models.billing import Invoice


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("ix_appointment_doctor_time", "doctor_id", "scheduled_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), index=True
    )
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"), index=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(
            AppointmentStatus,
            values_callable=lambda e: [m.value for m in e],
            native_enum=False,
            length=32,
        ),
        default=AppointmentStatus.scheduled,
    )
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="appointments")
    created_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[created_by_user_id])
    medical_records: Mapped[List["MedicalRecord"]] = relationship(
        "MedicalRecord", back_populates="appointment"
    )
    invoices: Mapped[List["Invoice"]] = relationship(
        "Invoice", back_populates="appointment"
    )
