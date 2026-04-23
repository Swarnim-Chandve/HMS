from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User, UserRole, Appointment
from app.repositories import appointment_repo, patient_repo, doctor_repo
from app.schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentUpdate


def _to_out(a: Appointment) -> AppointmentOut:
    return AppointmentOut.model_validate(a)


def _load(db: Session, appt_id: int) -> Appointment | None:
    return appointment_repo.get_by_id(db, appt_id)


def _scope(
    user: User, db: Session
) -> tuple[int | None, int | None, bool]:
    """
    Returns (filter_patient_id, filter_doctor_id, is_all).
    """
    if user.role in (UserRole.admin, UserRole.receptionist):
        return None, None, True
    if user.role == UserRole.patient:
        p = patient_repo.get_by_user_id(db, user.id)
        if not p:
            return -1, None, False
        return p.id, None, False
    if user.role == UserRole.doctor:
        d = doctor_repo.get_by_user_id(db, user.id)
        if not d:
            return None, -1, False
        return None, d.id, False
    return None, None, False


def list_appointments(
    db: Session, user: User, *, skip: int, limit: int
) -> tuple[list[AppointmentOut], int]:
    fp, fd, is_all = _scope(user, db)
    if not is_all and (fp == -1 or fd == -1):
        return [], 0
    if is_all:
        rows, total = appointment_repo.list_all(db, skip=skip, limit=limit)
    else:
        rows, total = appointment_repo.list_for_user_scope(
            db, patient_id=fp, doctor_id=fd, skip=skip, limit=limit
        )
    return [_to_out(x) for x in rows], total


def get_appointment(db: Session, user: User, appt_id: int) -> AppointmentOut:
    a = _load(db, appt_id)
    if not a:
        raise HTTPException(404, "Appointment not found")
    if user.role in (UserRole.admin, UserRole.receptionist):
        return _to_out(a)
    if user.role == UserRole.patient:
        p = patient_repo.get_by_user_id(db, user.id)
        if p and a.patient_id == p.id:
            return _to_out(a)
    if user.role == UserRole.doctor:
        d = doctor_repo.get_by_user_id(db, user.id)
        if d and a.doctor_id == d.id:
            return _to_out(a)
    raise HTTPException(403, "Not allowed")


def create_appointment(
    db: Session, user: User, data: AppointmentCreate
) -> AppointmentOut:
    if user.role in (UserRole.admin, UserRole.receptionist):
        pass
    elif user.role == UserRole.patient:
        p = patient_repo.get_by_user_id(db, user.id)
        if not p or p.id != data.patient_id:
            raise HTTPException(403, "Can only book for your own account")
    else:
        raise HTTPException(403, "Not allowed")
    if not patient_repo.get_by_id(db, data.patient_id):
        raise HTTPException(400, "Invalid patient_id")
    if not doctor_repo.get_by_id(db, data.doctor_id):
        raise HTTPException(400, "Invalid doctor_id")
    if appointment_repo.conflicting_window(
        db, doctor_id=data.doctor_id, scheduled_at=data.scheduled_at
    ):
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="Doctor has another appointment in that time window"
        )
    a = appointment_repo.create(
        db,
        patient_id=data.patient_id,
        doctor_id=data.doctor_id,
        scheduled_at=data.scheduled_at,
        reason=data.reason,
        created_by_user_id=user.id,
    )
    a = _load(db, a.id)
    if not a:
        raise HTTPException(500, "Create failed")
    return _to_out(a)


def update_appointment(
    db: Session, user: User, appt_id: int, data: AppointmentUpdate
) -> AppointmentOut:
    a = _load(db, appt_id)
    if not a:
        raise HTTPException(404, "Appointment not found")
    if user.role in (UserRole.admin, UserRole.receptionist):
        pass
    elif user.role == UserRole.patient:
        p = patient_repo.get_by_user_id(db, user.id)
        if not p or a.patient_id != p.id:
            raise HTTPException(403, "Not allowed")
    elif user.role == UserRole.doctor:
        d = doctor_repo.get_by_user_id(db, user.id)
        if not d or a.doctor_id != d.id:
            raise HTTPException(403, "Not allowed")
    else:
        raise HTTPException(403, "Not allowed")
    if data.scheduled_at is not None:
        if appointment_repo.conflicting_window(
            db,
            doctor_id=a.doctor_id,
            scheduled_at=data.scheduled_at,
            exclude_appointment_id=a.id,
        ):
            raise HTTPException(409, "Time conflict")
        a.scheduled_at = data.scheduled_at
    if data.status is not None:
        a.status = data.status
    if data.reason is not None:
        a.reason = data.reason
    a = appointment_repo.save(db, a)
    return _to_out(a)


def delete_appointment(db: Session, user: User, appt_id: int) -> None:
    a = _load(db, appt_id)
    if not a:
        raise HTTPException(404, "Appointment not found")
    if user.role not in (UserRole.admin, UserRole.receptionist):
        raise HTTPException(403, "Not allowed")
    appointment_repo.delete(db, a)
