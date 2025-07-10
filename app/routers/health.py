from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/healthz", summary="헬스체크")
async def health_check():
    return {"status": "ok", "env": settings.APP_ENV}
