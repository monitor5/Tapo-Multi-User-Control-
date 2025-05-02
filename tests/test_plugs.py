import logging
from fastapi import FastAPI
import uvicorn

from app.config import settings
from app.routers import health, auth, plugs

# 로깅 설정
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))

# FastAPI 애플리케이션 인스턴스 (모듈 레벨 변수로 노출)
app = FastAPI(
    title="Tapo Control API",
    debug=settings.DEBUG
)

# 엔드포인트 등록
app.include_router(health.router)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(plugs.router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
