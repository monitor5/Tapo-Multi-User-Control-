from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from app.config import settings
from app.db import get_session
from app.models import User

# OAuth2 인증 스키마 정의
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user_from_header(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_session),
) -> User:
    """
    Authorization 헤더의 Bearer 토큰을 검증해서 User 객체를 반환합니다.
    실패 시 401 예외를 던집니다.
    """
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
    return user

def get_admin_user(current_user: User = Depends(get_current_user_from_header)) -> User:
    """
    현재 사용자가 관리자 권한을 가지고 있는지 확인합니다.
    관리자가 아닐 경우 403 예외를 던집니다.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"관리자 권한 체크: 사용자 {current_user.username}, 역할: {current_user.role}")
    
    if current_user.role != "admin":
        logger.warning(f"관리자 권한 없음: 사용자 {current_user.username}, 역할: {current_user.role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )
    
    logger.info(f"관리자 권한 확인됨: {current_user.username}")
    return current_user 