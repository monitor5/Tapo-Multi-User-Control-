# app/models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base



class User(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    role     = Column(String(10), default="user")

    # Add the reverse relationship here
    plug_sessions = relationship("PlugSession", back_populates="user")


class PlugSession(Base):
    __tablename__ = "plug_sessions"

    id = Column(Integer, primary_key=True, index=True)
    plug_name = Column(String(50), ForeignKey("plugs.name"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)

    plug = relationship("Plug", back_populates="sessions")
    user = relationship("User", back_populates="plug_sessions")


class Plug(Base):
    __tablename__ = "plugs"

    name = Column(String(50), primary_key=True)
    ip = Column(String(50), nullable=False)

    sessions = relationship("PlugSession", back_populates="plug")