#!/usr/bin/env python
# migrate_db.py - 데이터베이스 스키마 업데이트 스크립트

import os
import sys
import sqlite3
from sqlalchemy import create_engine, text
from app.db import engine
from app.models import Base

def backup_database():
    """기존 데이터베이스 백업"""
    db_path = "users.db"
    backup_path = "users.db.bak"
    
    if os.path.exists(db_path):
        print(f"기존 데이터베이스 백업 중... ({db_path} -> {backup_path})")
        try:
            with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            print("백업 완료!")
        except Exception as e:
            print(f"백업 실패: {str(e)}")
            sys.exit(1)

def export_data():
    """기존 데이터베이스에서 데이터 추출"""
    try:
        print("기존 데이터 추출 중...")
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        
        # 테이블 존재 여부 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        tables = [t[0] for t in tables]
        
        data = {}
        
        if "users" in tables:
            cursor.execute("SELECT id, username, hashed_password, role FROM users")
            data["users"] = cursor.fetchall()
        
        if "plugs" in tables:
            cursor.execute("SELECT name, ip FROM plugs")
            data["plugs"] = cursor.fetchall()
        
        if "plug_sessions" in tables:
            cursor.execute("SELECT id, plug_name, user_id, started_at FROM plug_sessions")
            data["plug_sessions"] = cursor.fetchall()
        
        conn.close()
        print(f"데이터 추출 완료: {sum(len(v) for v in data.values())} 건")
        return data
    except Exception as e:
        print(f"데이터 추출 실패: {str(e)}")
        sys.exit(1)

def recreate_schema():
    """스키마 재생성"""
    try:
        print("데이터베이스 스키마 재생성 중...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("스키마 재생성 완료!")
    except Exception as e:
        print(f"스키마 재생성 실패: {str(e)}")
        sys.exit(1)

def import_data(data):
    """데이터 재삽입"""
    try:
        print("데이터 재삽입 중...")
        conn = engine.connect()
        
        # 사용자 데이터 삽입
        if "users" in data and data["users"]:
            for user in data["users"]:
                conn.execute(
                    text("INSERT INTO users (id, username, hashed_password, role) VALUES (:id, :username, :hashed_password, :role)"),
                    {"id": user[0], "username": user[1], "hashed_password": user[2], "role": user[3] if len(user) > 3 else "user"}
                )
        
        # 플러그 데이터 삽입
        if "plugs" in data and data["plugs"]:
            for plug in data["plugs"]:
                conn.execute(
                    text("INSERT INTO plugs (name, ip) VALUES (:name, :ip)"),
                    {"name": plug[0], "ip": plug[1]}
                )
        
        # 세션 데이터 삽입
        if "plug_sessions" in data and data["plug_sessions"]:
            for session in data["plug_sessions"]:
                conn.execute(
                    text("INSERT INTO plug_sessions (id, plug_name, user_id, started_at) VALUES (:id, :plug_name, :user_id, :started_at)"),
                    {"id": session[0], "plug_name": session[1], "user_id": session[2], "started_at": session[3]}
                )
        
        conn.commit()
        conn.close()
        print("데이터 재삽입 완료!")
    except Exception as e:
        print(f"데이터 재삽입 실패: {str(e)}")
        sys.exit(1)

def main():
    print("=== 데이터베이스 마이그레이션 시작 ===")
    
    # 사용자 확인
    confirm = input("데이터베이스 스키마를 업데이트합니다. 계속하시겠습니까? (y/n): ")
    if confirm.lower() != 'y':
        print("마이그레이션이 취소되었습니다.")
        return
    
    # 데이터베이스 백업
    backup_database()
    
    # 기존 데이터 추출
    data = export_data()
    
    # 스키마 재생성
    recreate_schema()
    
    # 데이터 재삽입
    import_data(data)
    
    print("=== 데이터베이스 마이그레이션 완료 ===")

if __name__ == "__main__":
    main() 