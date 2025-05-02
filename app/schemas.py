# app/schemas.py
from typing import List, Optional
from pydantic import BaseModel

class PlugInfo(BaseModel):
    name: str
    ip: str
    status: Optional[bool]      # None = 통신 실패
    active_users: int
    users: List[str]            # 반드시 포함해야 버튼 전환(iUse 계산)이 동작합니다

class PlugStatus(BaseModel):
    name: str
    status: bool
    active_users: int
    users: Optional[List[str]] = None  # 사용자 목록도 포함하여 UI에서 버튼 활성화 판단에 사용
