from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.repositories import medical_record_repo, patient_repo, doctor_repo
from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordOut,
    MedicalRecordUpdate,
)


def _to_out(r) -> MedicalRecordOut:
    return MedicalRecordOut.model_validate(r)


def list_records(
    db: Session,
    user: User,
    *,
    patient_id: int | None,
    skip: int,
    limit: int,
) -> tuple[list[MedicalRecordOut], int]:
    if user.role == UserRole.patient:
        p = patient_repo.get_by_user_id(db, user.id)
        if not p:
            return [], 0
        patient_id = p.id
        rows, total = medical_record_repo.list_by_patient(
            db, patient_id, skip=skip, limit=limit
        )
    elif user.role in (UserRole.admin, UserRole.doctor):
        if patient_id is not None:
            rows, total = medical_record_repo.list_by_patient(
                db, patient_id, skip=skip, limit=limit
            )
        else:
            if user.role == UserRole.doctor:
                raise HTTPException(400, "Doctors must supply patient_id filter")
            rows, total = medical_record_repo.list_all(db, skip=skip, limit=limit)
    else:
        raise HTTPException(403, "Not allowed")
    return [_to_out(x) for x in rows], total


def get_record(db: Session, user: User, record_id: int) -> MedicalRecordOut:
    r = medical_record_repo.get_by_id(db, record_id)
    if not r:
        raise HTTPException(404, "Record not found")
    if user.role == UserRole.patient:
        p = patient_repo.get_by_user_id(db, user.id)
        if not p or r.patient_id != p.id:
            raise HTTPException(403, "Not allowed")
        return _to_out(r)
    if user.role == UserRole.doctor:
        d = doctor_repo.get_by_user_id(db, user.id)
        if not d or r.doctor_id != d.id:
            raise HTTPException(403, "Not allowed")
        return _to_out(r)
    if user.role == UserRole.admin:
        return _to_out(r)
    raise HTTPException(403, "Not allowed")


def create_record(
    db: Session, user: User, data: MedicalRecordCreate
) -> MedicalRecordOut:
    if user.role not in (UserRole.admin, UserRole.doctor):
        raise HTTPException(403, "Not allowed")
    if user.role == UserRole.doctor:
        d = doctor_repo.get_by_user_id(db, user.id)
        if not d or d.id != data.doctor_id:
            raise HTTPException(403, "Can only create records as yourself")
    if not patient_repo.get_by_id(db, data.patient_id):
        raise HTTPException(400, "Invalid patient")
    if not doctor_repo.get_by_id(db, data.doctor_id):
        raise HTTPException(400, "Invalid doctor")
    r = medical_record_repo.create(
        db,
        patient_id=data.patient_id,
        doctor_id=data.doctor_id,
        appointment_id=data.appointment_id,
        diagnosis=data.diagnosis,
        notes=data.notes,
        prescription=data.prescription,
    )
    r = medical_record_repo.get_by_id(db, r.id)
    if not r:
        raise HTTPException(500, "Create failed")
    return _to_out(r)


def update_record(
    db: Session, user: User, record_id: int, data: MedicalRecordUpdate
) -> MedicalRecordOut:
    r = medical_record_repo.get_by_id(db, record_id)
    if not r:
        raise HTTPException(404, "Record not found")
    if user.role == UserRole.doctor:
        d = doctor_repo.get_by_user_id(db, user.id)
        if not d or r.doctor_id != d.id:
            raise HTTPException(403, "Not allowed")
    elif user.role != UserRole.admin:
        raise HTTPException(403, "Not allowed")
    if data.diagnosis is not None:
        r.diagnosis = data.diagnosis
    if data.notes is not None:
        r.notes = data.notes
    if data.prescription is not None:
        r.prescription = data.prescription
    if data.appointment_id is not None:
        r.appointment_id = data.appointment_id
    r = medical_record_repo.save(db, r)
    return _to_out(r)


def delete_record(db: Session, user: User, record_id: int) -> None:
    if user.role != UserRole.admin:
        raise HTTPException(403, "Not allowed")
    r = medical_record_repo.get_by_id(db, record_id)
    if not r:
        raise HTTPException(404, "Record not found")
    medical_record_repo.delete(db, r)
