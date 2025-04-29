LABEL authors="uhyun"
# Dockerfile
FROM python:3.13-slim

WORKDIR /app

# 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 코드 복사
COPY . .

# 포트 노출
EXPOSE 5005

# Gunicorn으로 프로덕션 모드 실행
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5005", "app:app"]

ENTRYPOINT ["top", "-b"]