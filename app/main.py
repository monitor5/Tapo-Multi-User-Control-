# app/main.py
import logging, uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import init_db
from app.routers import health, auth, plugs
from app.routers.ui import ui
from app.exceptions import BaseAPIException

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, logging.INFO))

# FastAPI 앱 설정 - Swagger UI에서 인증을 위한 보안 스키마 추가
app = FastAPI(
    title="Tapo Control API", 
    debug=settings.DEBUG,
    swagger_ui_parameters={"persistAuthorization": True},
    openapi_tags=[
        {"name": "auth", "description": "인증 관련 API"},
        {"name": "plugs", "description": "스마트 플러그 제어 API"}
    ]
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Run database migrations / seeding when the application starts
@app.on_event("startup")
def _startup_event():
    """Initialise database and seed admin user on application startup."""
    init_db()

@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )

app.include_router(health.router)           # /healthz
app.include_router(auth.router, prefix="/auth")
app.include_router(plugs.router)            # /plugs/…
app.include_router(ui)                      # /login, /
