# app/routers/ui.py
from fastapi import APIRouter, Request, Header, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import logging

from app.config import settings
from app.db import get_session
from app.models import User

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")
ui = APIRouter()


@ui.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@ui.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(
    request: Request, 
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_session)
):
    # 사용자 이름과 역할 추출 (Authorization 헤더에서)
    username = ""
    user_role = "user"
    logger.info(f"대시보드 접근: 헤더 {authorization}")
    
    # 1. Authorization 헤더에서 토큰 확인
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        logger.info(f"헤더에서 Bearer 토큰 발견: {token[:10]}...")
    
    # 2. 쿠키에서 토큰 확인 (백업)
    if not token and 'access_token' in request.cookies:
        token = request.cookies.get('access_token')
        logger.info(f"쿠키에서 토큰 발견: {token[:10]}...")
    
    # 토큰 디코딩 시도
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username = payload.get("sub", "")
            logger.info(f"토큰 디코딩 성공: 사용자 '{username}'")
            
            # DB에서 사용자 역할 조회
            if username:
                user = db.query(User).filter_by(username=username).first()
                if user:
                    user_role = user.role or "user"
                    logger.info(f"사용자 역할: {user_role}")
                    
        except JWTError as e:
            logger.error(f"토큰 디코딩 실패: {str(e)}")
    else:
        logger.warning("토큰을 찾을 수 없음")
    
    # 디버깅용 로그
    logger.info(f"UI 렌더링: 템플릿에 전달하는 사용자명: '{username}', 역할: '{user_role}'")
    
    # username과 user_role을 템플릿에 전달
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": username or "",  # None일 경우 빈 문자열로
        "user_role": user_role
    })


@ui.get("/user", response_class=HTMLResponse, include_in_schema=False)
async def user_page(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_session)
):
    """사용자 정보 페이지"""
    # 토큰에서 사용자 정보 추출
    username = ""
    user_role = "user"
    created_at = None
    
    # 1. Authorization 헤더에서 토큰 확인
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    
    # 2. 쿠키에서 토큰 확인 (백업)
    if not token and 'access_token' in request.cookies:
        token = request.cookies.get('access_token')
    
    # 토큰이 없으면 로그인 페이지로 리다이렉트
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    
    # 토큰 디코딩 및 사용자 정보 조회
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub", "")
        
        if username:
            # DB에서 사용자 정보 조회
            user = db.query(User).filter_by(username=username).first()
            if user:
                user_role = user.role or "user"
                # created_at은 현재 모델에 없으므로 None으로 유지
                logger.info(f"사용자 페이지 접근: {username} (권한: {user_role})")
            else:
                logger.warning(f"DB에서 사용자를 찾을 수 없음: {username}")
        else:
            logger.warning("토큰에서 사용자명을 추출할 수 없음")
            return RedirectResponse(url="/login", status_code=302)
            
    except JWTError as e:
        logger.error(f"토큰 디코딩 실패: {str(e)}")
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("user.html", {
        "request": request,
        "username": username,
        "user_role": user_role,
        "created_at": created_at
    })


@ui.get("/admin", response_class=HTMLResponse, include_in_schema=False)
async def admin_page(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_session)
):
    """관리자 페이지"""
    # 토큰에서 사용자 정보 추출
    username = ""
    user_role = "user"
    
    # 1. Authorization 헤더에서 토큰 확인
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    
    # 2. 쿠키에서 토큰 확인 (백업)
    if not token and 'access_token' in request.cookies:
        token = request.cookies.get('access_token')
    
    # 토큰이 없으면 로그인 페이지로 리다이렉트
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    
    # 토큰 디코딩 및 사용자 정보 조회
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub", "")
        
        if username:
            # DB에서 사용자 정보 조회
            user = db.query(User).filter_by(username=username).first()
            if user:
                user_role = user.role or "user"
                logger.info(f"관리자 페이지 접근 시도: {username} (권한: {user_role})")
                
                # 관리자 권한 확인
                if user_role != "admin":
                    logger.warning(f"관리자 권한 없음: {username}")
                    return RedirectResponse(url="/", status_code=302)
            else:
                logger.warning(f"DB에서 사용자를 찾을 수 없음: {username}")
                return RedirectResponse(url="/login", status_code=302)
        else:
            logger.warning("토큰에서 사용자명을 추출할 수 없음")
            return RedirectResponse(url="/login", status_code=302)
            
    except JWTError as e:
        logger.error(f"토큰 디코딩 실패: {str(e)}")
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "username": username,
        "user_role": user_role
    })
