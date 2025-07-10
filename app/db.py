# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./users.db"      # 나중에 postgres://... 로만 변경

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 전용 옵션
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

Base = declarative_base()

def create_admin_user():
    """환경변수에서 관리자 계정 정보를 읽어 DB에 생성/업데이트"""
    from app.config import settings
    from app.models import User
    from passlib.context import CryptContext
    
    # 관리자 계정 정보가 환경변수에 없으면 스킵
    if not settings.ADMIN_USERNAME or not settings.ADMIN_PASSWORD:
        logger.info("관리자 계정 환경변수가 설정되지 않음 (ADMIN_USERNAME, ADMIN_PASSWORD)")
        return
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    with SessionLocal() as db:
        try:
            # 기존 관리자 계정 확인
            admin_user = db.query(User).filter_by(username=settings.ADMIN_USERNAME).first()
            
            if admin_user:
                # 기존 계정이 있으면 비밀번호와 권한 업데이트
                admin_user.hashed_password = pwd_context.hash(settings.ADMIN_PASSWORD)
                admin_user.role = "admin"
                logger.info(f"관리자 계정 업데이트: {settings.ADMIN_USERNAME}")
            else:
                # 새 관리자 계정 생성
                admin_user = User(
                    username=settings.ADMIN_USERNAME,
                    hashed_password=pwd_context.hash(settings.ADMIN_PASSWORD),
                    role="admin"
                )
                db.add(admin_user)
                logger.info(f"새 관리자 계정 생성: {settings.ADMIN_USERNAME}")
            
            db.commit()
            logger.info("관리자 계정 설정 완료")
            
        except Exception as e:
            logger.error(f"관리자 계정 생성/업데이트 실패: {str(e)}")
            db.rollback()

def init_db() -> None:
    """애플리케이션 시작 시 한 번 호출—모든 테이블 생성 및 관리자 계정 설정"""
    import app.models  # noqa: F401  (User 모델 import)
    Base.metadata.create_all(bind=engine)
    
    # 관리자 계정 생성/업데이트
    create_admin_user()

# FastAPI 의존성
def get_session() -> Session:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
