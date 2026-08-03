
# import random
# import string
# from datetime import datetime

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy import select
# from sqlalchemy.orm import Session

# from app.database import get_db
# from app.models.complaint import Complaint, ComplaintStatus
# from app.schemas.complaint import ComplaintCommitRequest, ComplaintOut

# router = APIRouter(
#     prefix="/api/complaints",
#     tags=["complaints"],
# )


# def _generate_ref() -> str:
#     return f"CC-{datetime.utcnow().year}-{''.join(random.choices(string.digits, k=5))}"


# @router.post("", response_model=ComplaintOut, status_code=201)
# def commit_complaint(
#     payload: ComplaintCommitRequest,
#     db: Session = Depends(get_db),
# ):
#     """
#     'Commit to QMS Ledger' -- persists the reviewed/edited form as a new
#     complaint record.

#     Also runs a lightweight duplicate check against existing complaints
#     with the same product and batch number.
#     """
#     duplicate = None

#     if payload.product_name and payload.batch_number:
#         stmt = select(Complaint).where(
#             Complaint.product_name == payload.product_name,
#             Complaint.batch_number == payload.batch_number,
#         )

#         existing = db.execute(stmt).scalars().first()

#         if existing:
#             duplicate = existing.id

#     complaint = Complaint(
#         complaint_ref=_generate_ref(),
#         status=ComplaintStatus.committed,
#         ai_duplicate_of=duplicate,
#         **payload.model_dump(exclude={"ai_duplicate_of"}),
#     )

#     db.add(complaint)
#     db.commit()
#     db.refresh(complaint)

#     return complaint


# @router.get("", response_model=list[ComplaintOut])
# def list_complaints(db: Session = Depends(get_db)):
#     return (
#         db.execute(
#             select(Complaint).order_by(Complaint.created_at.desc())
#         )
#         .scalars()
#         .all()
#     )


# @router.get("/{complaint_id}", response_model=ComplaintOut)
# def get_complaint(
#     complaint_id: str,
#     db: Session = Depends(get_db),
# ):
#     complaint = db.get(Complaint, complaint_id)

#     if not complaint:
#         raise HTTPException(
#             status_code=404,
#             detail="Complaint not found",
#         )

#     return complaint



import random
import string
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.complaint import Complaint, ComplaintStatus
from app.schemas.complaint import ComplaintCommitRequest, ComplaintOut


router = APIRouter(
    prefix="/api/complaints",
    tags=["complaints"],
)


def _generate_ref() -> str:
    """Generate a unique complaint reference."""
    year = datetime.now(timezone.utc).year
    number = "".join(random.choices(string.digits, k=5))
    return f"CC-{year}-{number}"


@router.post(
    "",
    response_model=ComplaintOut,
    status_code=201,
)
def commit_complaint(
    payload: ComplaintCommitRequest,
    db: Session = Depends(get_db),
):
    """
    Save a reviewed complaint to the QMS ledger.

    A lightweight duplicate check is performed using the
    product name and batch number.
    """

    duplicate = None

    if payload.product_name and payload.batch_number:
        stmt = select(Complaint).where(
            Complaint.product_name == payload.product_name,
            Complaint.batch_number == payload.batch_number,
        )

        existing = db.execute(stmt).scalars().first()

        if existing:
            duplicate = existing.id

    complaint_data = payload.model_dump(
        exclude={"ai_duplicate_of"},
    )

    complaint = Complaint(
        complaint_ref=_generate_ref(),
        status=ComplaintStatus.committed,
        ai_duplicate_of=duplicate,
        **complaint_data,
    )

    try:
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
    except Exception:
        db.rollback()
        raise

    return complaint


@router.get(
    "",
    response_model=list[ComplaintOut],
)
def list_complaints(
    db: Session = Depends(get_db),
):
    """Return all complaints ordered by newest first."""

    stmt = select(Complaint).order_by(
        Complaint.created_at.desc()
    )

    return db.execute(stmt).scalars().all()


@router.get(
    "/{complaint_id}",
    response_model=ComplaintOut,
)
def get_complaint(
    complaint_id: str,
    db: Session = Depends(get_db),
):
    """Return a single complaint by ID."""

    complaint = db.get(
        Complaint,
        complaint_id,
    )

    if complaint is None:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found",
        )

    return complaint
