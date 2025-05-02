# create_user.py
import getpass, sys, re
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models import Base, User     # ← User, Base 둘 다 import
from app.db import engine             # 기존 engine 재사용

# ⭐️ 1) 테이블이 없으면 먼저 만든다
Base.metadata.create_all(bind=engine)     # ← 이 한 줄 추가

ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 입력값 검증 - 알파벳, 숫자, 일부 특수문자만 허용
def validate_username(username):
    if not username:
        return False, "사용자 ID를 입력해주세요."
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        return False, "사용자 ID는 영문자, 숫자, 밑줄(_), 점(.), 하이픈(-)만 사용 가능합니다."
    return True, ""

# 사용자 입력 처리 함수
def get_safe_input(prompt):
    while True:
        try:
            value = input(prompt).strip()
            # 입력값을 명시적으로 UTF-8로 인코딩 후 다시 디코딩하여 문자열 검증
            encoded = value.encode('utf-8')
            decoded = encoded.decode('utf-8')
            return decoded
        except UnicodeError as e:
            print(f"오류: 입력에 잘못된 문자가 포함되어 있습니다. ({str(e)})")
            print("다시 입력해주세요.")

# 입력 받기
username = get_safe_input("새 사용자 ID: ")
is_valid, error_msg = validate_username(username)

if not is_valid:
    sys.exit(error_msg)

try:
    password = getpass.getpass("비밀번호: ")
except UnicodeError:
    sys.exit("비밀번호에 지원하지 않는 문자가 포함되어 있습니다.")

try:
    with Session(engine) as s:
        if s.query(User).filter_by(username=username).first():
            sys.exit("이미 존재하는 ID입니다.")
        s.add(User(username=username, hashed_password=ctx.hash(password)))
        s.commit()
        print("✅ 사용자 추가 완료")
except Exception as e:
    print(f"오류 발생: {str(e)}")
    sys.exit("사용자 추가에 실패했습니다.")
