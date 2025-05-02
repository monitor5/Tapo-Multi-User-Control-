# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from contextlib import contextmanager

DATABASE_URL = "sqlite:///./users.db"      # 나중에 postgres://... 로만 변경

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 전용 옵션
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

Base = declarative_base()

def init_db() -> None:
    """애플리케이션 시작 시 한 번 호출—모든 테이블 생성"""
    import app.models  # noqa: F401  (User 모델 import)
    Base.metadata.create_all(bind=engine)

# FastAPI 의존성
def get_session() -> Session:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
