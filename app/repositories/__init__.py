from app.repositories import user_repo
from app.repositories import patient_repo
from app.repositories import doctor_repo
from app.repositories import appointment_repo
from app.repositories import medical_record_repo
from app.repositories import billing_repo

__all__ = [
    "user_repo",
    "patient_repo",
    "doctor_repo",
    "appointment_repo",
    "medical_record_repo",
    "billing_repo",
]
