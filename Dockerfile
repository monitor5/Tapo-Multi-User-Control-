
# Dockerfile
FROM python:3.12-slim

LABEL authors="uhyun"

WORKDIR /app

# 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 코드 복사
COPY . .

# 포트 노출
EXPOSE 5005

# Gunicorn으로 프로덕션 모드 실행
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "5005", \
     "--reload"]

# 컨테이너 안에서 계정 생성
#RUN docker compose exec web python create_user.py
