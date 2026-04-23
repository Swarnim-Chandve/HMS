from app.models import Doctor, Patient
from app.schemas.patient import PatientOut
from app.schemas.doctor import DoctorOut


def patient_to_out(p: Patient) -> PatientOut:
    u = p.user
    return PatientOut(
        id=p.id,
        user_id=p.user_id,
        email=u.email,
        full_name=u.full_name,
        date_of_birth=p.date_of_birth,
        phone=p.phone,
        address=p.address,
        emergency_contact=p.emergency_contact,
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


def doctor_to_out(d: Doctor) -> DoctorOut:
    u = d.user
    return DoctorOut(
        id=d.id,
        user_id=d.user_id,
        email=u.email,
        full_name=u.full_name,
        specialization=d.specialization,
        license_number=d.license_number,
        department=d.department,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )
