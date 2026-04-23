from fastapi import APIRouter

from app.api.v1.routes import auth, patients, doctors, appointments, records, billing

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(patients.router)
api_router.include_router(doctors.router)
api_router.include_router(appointments.router)
api_router.include_router(records.router)
api_router.include_router(billing.router)
