from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.billing import (
    InvoiceCreate,
    InvoiceOut,
    InvoiceStatusUpdate,
)
from app.services import billing_service

router = APIRouter(prefix="/invoices", tags=["billing"])


@router.get("", response_model=dict)
def list_invoices(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    patient_id: int | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
) -> dict:
    items, total = billing_service.list_invoices(
        db, user, patient_id=patient_id, skip=skip, limit=limit
    )
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> InvoiceOut:
    return billing_service.get_invoice(db, user, invoice_id)


@router.post(
    "", response_model=InvoiceOut, status_code=status.HTTP_201_CREATED
)
def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> InvoiceOut:
    return billing_service.create_invoice(db, user, data)


@router.patch("/{invoice_id}/status", response_model=InvoiceOut)
def update_invoice_status(
    invoice_id: int,
    data: InvoiceStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> InvoiceOut:
    return billing_service.update_status(db, user, invoice_id, data)
