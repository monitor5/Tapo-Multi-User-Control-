# app/routers/auth.py
import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import User
from app.services.auth import authenticate_user, create_access_token
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
