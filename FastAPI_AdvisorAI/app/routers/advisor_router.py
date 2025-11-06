# app/routers/advisor_router.py
from fastapi import APIRouter
from app.models.schemas import ClientProfile
from app.controllers.advisor_controller import get_advice
from app.core.utils import get_utc_timestamp

router = APIRouter(prefix="/advisor", tags=["Advisor"])

@router.get("/health")
def health():
    return {"status": "ok", "timestamp": get_utc_timestamp()}

@router.post("/advise")
def advise(profile: ClientProfile):
    return get_advice(profile.dict())
