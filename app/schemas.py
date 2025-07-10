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

# 사용자 관리 관련 스키마들
class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    users: List[UserResponse]

class PasswordReset(BaseModel):
    new_password: str

# 플러그 권한 관련 스키마들
class PlugPermissionCreate(BaseModel):
    user_id: int
    plug_name: str

class PlugPermissionResponse(BaseModel):
    id: int
    user_id: int
    plug_name: str
    
    class Config:
        from_attributes = True

class UserWithPermissions(UserResponse):
    """권한 정보를 포함한 사용자 정보"""
    allowed_plugs: List[str] = []

class UserPermissionsResponse(BaseModel):
    users: List[UserWithPermissions]
