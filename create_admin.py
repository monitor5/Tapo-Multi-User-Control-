#!/usr/bin/env python3
"""
관리자 계정 생성 스크립트
"""

import os
import sys
from sqlalchemy.orm import Session

# 프로젝트 루트를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import get_session
from app.models import User
from app.services.auth import get_password_hash

def create_admin_user():
    """관리자 계정 생성"""
    
    # 사용자 입력 받기
    username = input("관리자 사용자명을 입력하세요: ").strip()
    if not username:
        print("사용자명은 필수입니다.")
        return False
    
    password = input("관리자 비밀번호를 입력하세요: ").strip()
    if not password:
        print("비밀번호는 필수입니다.")
        return False
    
    # 데이터베이스 세션 생성
    db = next(get_session())
    
    try:
        # 기존 사용자 확인
        existing_user = db.query(User).filter_by(username=username).first()
        if existing_user:
            print(f"사용자 '{username}'이 이미 존재합니다.")
            
            # 기존 사용자를 관리자로 업데이트할지 묻기
            update = input("기존 사용자를 관리자로 업데이트하시겠습니까? (y/N): ").strip().lower()
            if update == 'y':
                existing_user.role = "admin"
                existing_user.hashed_password = get_password_hash(password)
                db.commit()
                print(f"사용자 '{username}'이 관리자로 업데이트되었습니다.")
                return True
            else:
                print("취소되었습니다.")
                return False
        
        # 새 관리자 사용자 생성
        hashed_password = get_password_hash(password)
        admin_user = User(
            username=username,
            hashed_password=hashed_password,
            role="admin"
        )
        
        db.add(admin_user)
        db.commit()
        
        print(f"관리자 계정 '{username}'이 성공적으로 생성되었습니다.")
        return True
        
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()

def main():
    """메인 함수"""
    print("=== 관리자 계정 생성 ===")
    print()
    
    success = create_admin_user()
    
    if success:
        print()
        print("관리자 계정이 성공적으로 생성되었습니다.")
        print("이제 웹 인터페이스에 로그인하여 관리자 기능을 사용할 수 있습니다.")
        print("- 대시보드에서 '관리자 페이지' 버튼을 클릭하세요.")
        print("- 또는 직접 /admin 경로로 접속하세요.")
    else:
        print()
        print("관리자 계정 생성에 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main() 