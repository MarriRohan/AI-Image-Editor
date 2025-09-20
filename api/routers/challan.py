from fastapi import APIRouter, Depends
from api.auth import get_current_user

router = APIRouter()

@router.post("/issue-fine")
async def issue_fine(payload: dict, user=Depends(get_current_user)):
    return {"status": "mock", "payload": payload}
