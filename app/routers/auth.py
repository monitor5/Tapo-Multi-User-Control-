# app/routers/auth.py
import logging
from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import User, UserPlugPermission
from app.services.auth import authenticate_user, create_access_token, get_password_hash
from app.services.permissions import (
    get_all_users_with_permissions, 
    grant_plug_permission, 
    revoke_plug_permission
)
from app.services.pyp100 import pyp100_service
from app.schemas import (
    UserCreate, UserResponse, UserListResponse, PasswordReset,
    UserPermissionsResponse, PlugPermissionCreate
)
from app.dependencies import get_admin_user, get_current_user_from_header
from app.config import settings

router = APIRouter(tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/login", summary="로그인 및 JWT 토큰 발급")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_session),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "아이디 또는 비번이 틀렸습니다"
        )

    # 토큰 생성
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # 토큰 반환 (OAuth2 표준 형식)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout", summary="로그아웃 (클라이언트에서 토큰 폐기)")
def logout():
    # 서버에서는 stateless하게 동작하므로 실제 토큰 폐기는 없음
    # 클라이언트에서 토큰 삭제 필요
    return {"msg": "로그아웃 처리되었습니다"}


# 관리자 전용 API 엔드포인트들
@router.post("/admin/users", response_model=UserResponse, summary="사용자 생성 (관리자 전용)")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user)
):
    logger.info(f"사용자 생성 요청 수신: {user_data.username}, 역할: {user_data.role}, 관리자: {admin_user.username}")
    
    # 사용자명 중복 체크
    existing_user = db.query(User).filter_by(username=user_data.username).first()
    if existing_user:
        logger.warning(f"사용자명 중복: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자명입니다."
        )
    
    try:
        # 새 사용자 생성
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            hashed_password=hashed_password,
            role=user_data.role
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"관리자 {admin_user.username}가 새 사용자 {new_user.username}을 성공적으로 생성했습니다.")
        return new_user
        
    except Exception as e:
        logger.error(f"사용자 생성 중 오류: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/admin/users", response_model=UserListResponse, summary="사용자 목록 조회 (관리자 전용)")
def get_users(
    db: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user)
):
    logger.info(f"사용자 목록 조회 요청: 관리자 {admin_user.username}")
    try:
        users = db.query(User).all()
        logger.info(f"사용자 목록 조회 성공: {len(users)}명의 사용자")
        return UserListResponse(users=users)
    except Exception as e:
        logger.error(f"사용자 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/admin/users/{user_id}/password", summary="비밀번호 재설정 (관리자 전용)")
def reset_user_password(
    user_id: int,
    password_data: PasswordReset,
    db: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user)
):
    # 대상 사용자 조회
    target_user = db.query(User).filter_by(id=user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 비밀번호 재설정
    hashed_password = get_password_hash(password_data.new_password)
    target_user.hashed_password = hashed_password
    
    db.commit()
    
    logger.info(f"관리자 {admin_user.username}가 사용자 {target_user.username}의 비밀번호를 재설정했습니다.")
    return {"msg": f"사용자 {target_user.username}의 비밀번호가 재설정되었습니다."}


@router.delete("/admin/users/{user_id}", summary="사용자 삭제 (관리자 전용)")
def delete_user(
    user_id: int,
    db: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user)
):
    # 대상 사용자 조회
    target_user = db.query(User).filter_by(id=user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 자기 자신은 삭제할 수 없음
    if target_user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신은 삭제할 수 없습니다."
        )
    
    db.delete(target_user)
    db.commit()
    
    logger.info(f"관리자 {admin_user.username}가 사용자 {target_user.username}을 삭제했습니다.")
    return {"msg": f"사용자 {target_user.username}이 삭제되었습니다."}


# 플러그 권한 관리 API
@router.get("/admin/users/permissions", response_model=UserPermissionsResponse, 
           summary="사용자별 플러그 권한 조회 (관리자 전용)")
def get_users_permissions(
    db: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user)
):
    """모든 사용자와 그들의 플러그 권한을 조회"""
    logger.info(f"사용자 권한 목록 조회: 관리자 {admin_user.username}")
    
    try:
        users_with_permissions = get_all_users_with_permissions(db)
        return UserPermissionsResponse(users=users_with_permissions)
    except Exception as e:
        logger.error(f"사용자 권한 목록 조회 중 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 권한 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/admin/plugs", summary="사용 가능한 플러그 목록 조회 (관리자 전용)")
def get_available_plugs(
    admin_user: User = Depends(get_admin_user)
):
    """시스템에 등록된 모든 플러그 목록을 반환"""
    logger.info(f"플러그 목록 조회: 관리자 {admin_user.username}")
    
    plugs = [{"name": name, "ip": ip} for name, ip in pyp100_service.plugs.items()]
    return {"plugs": plugs}


@router.post("/admin/permissions/grant", summary="플러그 권한 부여 (관리자 전용)")
def grant_permission(
    permission_data: PlugPermissionCreate,
    db: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user)
):
    """사용자에게 특정 플러그 권한을 부여"""
    logger.info(f"플러그 권한 부여 요청: 관리자 {admin_user.username}, 사용자 ID {permission_data.user_id}, 플러그 {permission_data.plug_name}")
    
    # 사용자 존재 확인
    target_user = db.query(User).filter_by(id=permission_data.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 권한 부여
    if grant_plug_permission(permission_data.user_id, permission_data.plug_name, db):
        logger.info(f"관리자 {admin_user.username}가 사용자 {target_user.username}에게 플러그 {permission_data.plug_name} 권한을 부여했습니다.")
        return {"msg": f"사용자 {target_user.username}에게 플러그 {permission_data.plug_name} 권한이 부여되었습니다."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="권한 부여에 실패했습니다."
        )


@router.delete("/admin/permissions/revoke", summary="플러그 권한 회수 (관리자 전용)")
def revoke_permission(
    permission_data: PlugPermissionCreate,
    db: Session = Depends(get_session),
    admin_user: User = Depends(get_admin_user)
):
    """사용자의 특정 플러그 권한을 회수"""
    logger.info(f"플러그 권한 회수 요청: 관리자 {admin_user.username}, 사용자 ID {permission_data.user_id}, 플러그 {permission_data.plug_name}")
    
    # 사용자 존재 확인
    target_user = db.query(User).filter_by(id=permission_data.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    # 권한 회수
    if revoke_plug_permission(permission_data.user_id, permission_data.plug_name, db):
        logger.info(f"관리자 {admin_user.username}가 사용자 {target_user.username}의 플러그 {permission_data.plug_name} 권한을 회수했습니다.")
        return {"msg": f"사용자 {target_user.username}의 플러그 {permission_data.plug_name} 권한이 회수되었습니다."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="권한 회수에 실패했습니다."
        )


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_session),
) -> str:
    """
    Authorization 헤더의 Bearer 토큰을 검증해서 username(sub) 리턴.
    실패 시 401 예외를 던집니다.
    """
    from jose import JWTError, jwt
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise JWTError()
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # User 존재 여부 검증
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return username
