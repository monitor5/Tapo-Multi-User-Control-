#!/usr/bin/env python3
"""
Test script to create a user without interactive input
"""
import sys
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models import Base, User
from app.db import engine

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_user():
    """Create a test user for testing purposes"""
    test_username = "testuser"
    test_password = "testpass123"
    
    try:
        with Session(engine) as s:
            # Check if user already exists
            existing_user = s.query(User).filter_by(username=test_username).first()
            if existing_user:
                print(f"❌ User '{test_username}' already exists!")
                return False
            
            # Create new user
            new_user = User(
                username=test_username,
                hashed_password=ctx.hash(test_password),
                role="user"
            )
            s.add(new_user)
            s.commit()
            
            print(f"✅ 사용자 '{test_username}' 생성 완료!")
            print(f"✅ 비밀번호: {test_password}")
            print(f"✅ 역할: user")
            return True
            
    except Exception as e:
        print(f"❌ 사용자 생성 실패: {e}")
        return False

if __name__ == "__main__":
    success = create_test_user()
    sys.exit(0 if success else 1) 