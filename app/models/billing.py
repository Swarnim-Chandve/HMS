from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import InvoiceStatus

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.appointment import Appointment


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), index=True
    )
    appointment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(
            InvoiceStatus,
            values_callable=lambda e: [m.value for m in e],
            native_enum=False,
            length=32,
        ),
        default=InvoiceStatus.pending,
    )
    amount_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00")
    )
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    patient: Mapped["Patient"] = relationship("Patient", back_populates="invoices")
    appointment: Mapped[Optional["Appointment"]] = relationship(
        "Appointment", back_populates="invoices"
    )
    lines: Mapped[List["InvoiceLine"]] = relationship(
        "InvoiceLine", back_populates="invoice", cascade="all, delete-orphan"
    )


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"), index=True
    )
    description: Mapped[str] = mapped_column(String(500))
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1"))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    line_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00")
    )

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="lines")
