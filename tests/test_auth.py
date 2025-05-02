from fastapi import APIRouter, Depends
from typing import List
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/plugs",
    tags=["plugs"],
    dependencies=[Depends(get_current_user)]  # JWT 인증 필요
)

@router.get("/", summary="플러그 목록 조회 (인증 필요)")
async def list_plugs() -> List[dict]:
    """
    사용자별 플러그 목록을 반환합니다.
    나중에 PLUGS 환경변수 파싱 로직으로 대체 예정
    """
    return [{"name": "uhyun", "ip": "192.168.1.100"}]
