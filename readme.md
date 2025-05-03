# Tapo-Control 사용자 매뉴얼
> **버전** 0.2 (2025-05-02)  
> **대상** DevOps · 내부 사용자

---

## 목차
1. [개요]
2. [논리 아키텍처]
3. [인프라 아키텍처]
4. [사전 요구 사항]
5. [빠른 시작 (⏱ 3 분)]
6. [핵심 환경 변수 (.env)]
7. [프로젝트 구조]  
8. [관리자 계정 추가]
9. [주요 API] 
10. [문제 해결 FAQ]
11. [로드맵 (발췌)]

---

## 1 | 개요
TP-Link **Tapo 스마트 플러그**를 원격으로 제어해 워크스테이션 전원을 관리하는 **경량 FastAPI** 애플리케이션입니다.  
제어 라이브러리로는 [`plugp100`](https://github.com/petretiandrea/plugp100)를 사용합니다.

| 핵심 기능                          | 비고                                     |
|----------------------------------|----------------------------------------|
| JWT 로그인 / 토큰 발급               | bcrypt 해시 기반                          |
| 플러그 On · Off · Status REST API  | `plugp100` 라이브러리                    |
| SSR 웹 UI                         | Jinja2 + Bootstrap 5                   |
| CI 테스트                         | `pytest`                               |
| 컨테이너 배포                      | **Docker Compose**                     |

---

## 2 | 논리 아키텍처
![ChatGPT Image 2025년 5월 3일 오후 08_39_13](https://github.com/user-attachments/assets/a5d23fbd-857f-40f4-a843-efccfa6c94cd)
> 현재 컨테이너는 **uvicorn 단독** 구동입니다.  
> Gunicorn workers 전환은 로드맵 Sprint 4 항목입니다.

---

## 3 | 인프라 아키텍처

- **호스팅 환경**  
  - 베어메탈 또는 가상머신(VM) 상 Docker 환경  
  - Kubernetes 클러스터(선택 항목)  
- **네트워크 구성**  
  - 내부망: `82/TCP` 포트로 Nginx → FastAPI  
  - 방화벽: 80, 443, 5000–5005, 8000, 8080 허용  
  - VPN 또는 VPC 내 배포 권장  
- **확장성**  
  - Docker Compose → Kubernetes로 전환 시 Horizontal Pod Autoscaling 적용 가능  
  - Gunicorn worker 다중화로 동시 처리량 증가  
- **보안 & 인증**  
  - JWT 기반 인증  
  - Nginx에서 TLS 종료(HTTPS)  
  - 내부망 전용 통신, 외부 접근 시 VPN/IP 화이트리스트  
- **모니터링 & 로깅**  
  - Prometheus + Grafana 연동 (메트릭 수집)  
  - ELK 스택(Elasticsearch, Logstash, Kibana) 또는 Fluentd 로깅 집계  
  - Docker 로그 → 중앙집중형 로깅 서버 전송  
- **CI/CD 파이프라인**  
  - GitHub Actions 또는 GitLab CI  
  - 이미지 빌드 → Vulnerability 스캔 → Staging/Production 자동 배포  

---

## 4 | 사전 요구 사항

| 항목                 | 최소 버전     |
|---------------------|-------------|
| **Docker**          | 20.10+      |
| **docker-compose**  | 2.20+       |
| (개발) **Python**    | 3.12        |

---

## 5 | 빠른 시작 (⏱ 3 분)

```bash
git clone https://github.com/your-org/tapo-control.git
cd tapo-control

# ① 환경 변수
cp .env.example .env
python -m passlib.hash bcrypt -g      # 비밀번호 해시 생성 → .env에 입력

# ② 빌드 & 기동
docker compose up -d --build

# ③ 접속
open http://localhost:82          # nginx 프록시
open http://localhost:82/docs     # Swagger
````

---

## 6 | 핵심 환경 변수 (.env)

| 변수                    | 설명                       | 예시                  |
| --------------------- | ------------------------ | ------------------- |
| `ADMIN_USERNAME`      | 기본 관리자 ID                | `admin`             |
| `ADMIN_PASSWORD_HASH` | bcrypt 해시                | `$2b$12$…`          |
| `JWT_SECRET`          | 토큰 서명 키                  | `supersecret`       |
| `JWT_ALGORITHM`       | 알고리즘                     | `HS256`             |
| `APP_HOST`            | 내부 바인딩                   | `0.0.0.0`           |
| `APP_PORT`            | 컨테이너 내부 포트               | `5004`              |
| `TAPO_PLUGS`          | `이름=IP` 콤마 구분            | `ws01=192.168.1.31` |
| `LOG_LEVEL`           | `DEBUG / INFO / WARNING` | `INFO`              |

---

## 7 | 프로젝트 구조

```
tapo-control/
│
├─ app/
│   ├─ __init__.py
│   ├─ main.py          ▶ FastAPI entrypoint
│   ├─ config.py        ▶ Pydantic Settings
│   ├─ db.py            ▶ (추후 SQLite → Postgres)
│   ├─ models.py
│   ├─ schemas.py
│   ├─ dependencies.py
│   ├─ static/          ▶ JS · CSS
│   │   └─ js/login.js
│   └─ templates/       ▶ Jinja2 HTML
│
├─ data/                ▶ SQLite 파일
├─ logs/                ▶ 애플리케이션 로그
│
├─ nginx/
│   └─ nginx.conf       ▶ reverse-proxy (82)
│
├─ tests/               ▶ pytest 스위트
│   ├─ test_auth.py
│   └─ test_plugs.py
│
├─ create_user.py       ▶ 관리자 계정 CLI
├─ migrate_db.py        ▶ DB 스키마 초기화
├─ Dockerfile           ▶ python:3.12-slim + uvicorn
├─ docker-compose.yml   ▶ web & nginx
└─ requirements.txt
```

---

## 8 | 관리자 계정 추가

```bash
docker compose exec web python /app/create_user.py
# 프롬프트에 따라 username / password 입력
```

컨테이너 내부에서 DB에 기록되므로 `.env` 의 `ADMIN_PASSWORD_HASH` 는 **초기 1회**만 사용합니다.

---

## 9 | 주요 API

| 메서드    | 엔드포인트                       | 설명     |
| ------ | --------------------------- | ------ |
| `GET`  | `/healthz`                  | 헬스 체크  |
| `POST` | `/auth/login`               | JWT 발급 |
| `GET`  | `/plugs/`                   | 플러그 목록 |
| `POST` | `/plugs/{name}/on` / `/off` | 전원 제어  |
| `GET`  | `/plugs/{name}/status`      | 상태 조회  |

---

## 10 | 문제 해결 FAQ

| 증상                        | 조치                                   |
| ------------------------- | ------------------------------------ |
| 로그인 직후 다시 로그인 페이지         | 쿠키 SameSite 차단 여부 확인                 |
| `401 Unauthorized`        | JWT 만료 → 재로그인                        |
| `502 Bad Gateway` (nginx) | `docker compose ps` 로 web 컨테이너 상태 확인 |
| 플러그 제어 실패                 | `.env` IP, 디바이스 LAN 연결 확인            |

**로그 확인**

```bash
docker compose logs -f web    # FastAPI
docker compose logs -f nginx  # proxy
```

---

## 11 | 로드맵 (발췌)

| Sprint | 주요 항목                             | 상태     |
| ------ | --------------------------------- | ------ |
| 2      | 다중 플러그 동시 제어, Discord 알림          | ✅ 완료   |
| 3      | SQLite → Postgres, 역할별 권한         | 🛠 진행중 |
| 4      | HTTPS, Gunicorn workers, RBAC 고도화 | 계획     |

```
