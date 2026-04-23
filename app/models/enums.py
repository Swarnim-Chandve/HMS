import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"
    receptionist = "receptionist"


class AppointmentStatus(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"


class InvoiceStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    void = "void"
