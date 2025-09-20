from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
from api.models import SessionLocal, ViolationEvent
from api.auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
async def list_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    ev_type: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(ViolationEvent)
    if ev_type:
        q = q.filter(ViolationEvent.type == ev_type)
    total = q.count()
    items = q.order_by(ViolationEvent.id.desc()).offset((page-1)*page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": it.id,
                "type": it.type,
                "score": it.score,
                "plate_text": it.plate_text,
                "plate_conf": it.plate_conf,
                "speed_kph": it.speed_kph,
                "evidence_path": it.evidence_path,
                "evidence_plate_path": it.evidence_plate_path,
                "meta": it.meta,
                "created_at": it.created_at.isoformat(),
            } for it in items
        ]
    }
