# app/routers/ui.py
from fastapi import APIRouter, Request, Header, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from jose import JWTError, jwt
import logging

from app.config import settings

logger = logging.getLogger(__name__)
templates = Jinja2Templates(directory="app/templates")
ui = APIRouter()


@ui.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@ui.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(
    request: Request, 
    authorization: Optional[str] = Header(None)
):
    # 사용자 이름 추출 (Authorization 헤더에서)
    username = ""
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
        except JWTError as e:
            logger.error(f"토큰 디코딩 실패: {str(e)}")
    else:
        logger.warning("토큰을 찾을 수 없음")
    
    # 디버깅용 로그
    logger.info(f"UI 렌더링: 템플릿에 전달하는 사용자명: '{username}'")
    
    # username을 템플릿에 전달
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": username or ""  # None일 경우 빈 문자열로
    })
