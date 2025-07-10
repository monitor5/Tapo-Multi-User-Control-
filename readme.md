# 🔌 Tapo-Control 사용자 매뉴얼
> **버전** 0.9 (2025-07-10)  
> **대상** DevOps · 내부 사용자 · 시스템 관리자

---

## 📋 목차
1. [개요 및 주요 개선사항]
2. [논리 아키텍처]
3. [인프라 아키텍처]
4. [사전 요구 사항]
5. [빠른 시작 (⏱ 5 분)]
6. [핵심 환경 변수 (.env)]
7. [프로젝트 구조]
8. [사용자 관리]
9. [주요 API]
10. [웹 UI 가이드]
11. [문제 해결 FAQ]
12. [로드맵]

---

## 1 | 개요 및 주요 개선사항

TP-Link **Tapo 스마트 플러그**를 원격으로 제어해 워크스테이션 전원을 관리하는 **고급 FastAPI** 애플리케이션입니다.  
제어 라이브러리로는 [`plugp100`](https://github.com/petretiandrea/plugp100)를 사용합니다.

### 🆕 v0.9 주요 개선사항

| 기능 영역 | v0.2 → v0.9 개선사항 |
|----------|-------------------|
| **사용자 관리** | ✅ JWT 기반 인증 시스템 완전 구현<br>✅ 역할 기반 권한 관리 (Admin/User)<br>✅ 사용자별 플러그 접근 권한 제어 |
| **플러그 제어** | ✅ 다중 사용자 동시 사용 지원<br>✅ 사용 예약/해제 시스템<br>✅ 실시간 상태 모니터링 |
| **웹 인터페이스** | ✅ 반응형 대시보드 UI<br>✅ 관리자 전용 페이지<br>✅ 사용자 정보 페이지 |
| **데이터베이스** | ✅ SQLite 기반 사용자 관리<br>✅ 세션 추적 및 권한 관리<br>✅ 관계형 데이터 모델 |
| **보안** | ✅ JWT 토큰 인증<br>✅ bcrypt 비밀번호 해싱<br>✅ 권한 기반 API 접근 제어 |
| **배포** | ✅ Synology NAS 최적화<br>✅ Docker Compose 구성<br>✅ Nginx 리버스 프록시 |

### 🎯 핵심 기능

| 기능 | 설명 | 비고 |
|------|------|------|
| **JWT 인증** | 토큰 기반 로그인/로그아웃 | bcrypt 해시 기반 |
| **역할 관리** | Admin/User 역할 구분 | 권한별 기능 제한 |
| **플러그 제어** | On/Off/Status REST API | 다중 사용자 지원 |
| **세션 관리** | 사용자별 플러그 사용 추적 | 자동 정리 |
| **웹 UI** | Jinja2 + Bootstrap 5 | 반응형 디자인 |
| **권한 제어** | 플러그별 접근 권한 관리 | 세밀한 제어 |
| **모니터링** | 실시간 상태 및 로그 | 상세한 추적 |

---

## 2 | 논리 아키텍처

```
┌─────────────────┐    ┌─────────────────┐   
│   Web Browser   │    │   API Client    │   
└─────────┬───────┘    └─────────┬───────┘   
          │                      │           
          └──────────────────────┼
                                 │
                    ┌─────────────▼─────────────┐
                    │    Nginx (Port 84)        │
                    │   Reverse Proxy + SSL     │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │   FastAPI (Port 5011)     │
                    │   - JWT Authentication    │
                    │   - Role-based Access     │
                    │   - Session Management    │
                    └─────────────┬─────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
┌─────────▼─────────┐  ┌─────────▼─────────┐  ┌─────────▼─────────┐
│   Auth Service    │  │  Plug Service     │  │  Permission Svc   │
│   - Login/Logout  │  │  - On/Off/Status  │  │  - Access Control │
│   - JWT Tokens    │  │  - Multi-user     │  │  - User Roles     │
└───────────────────┘  └───────────────────┘  └───────────────────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │    SQLite Database        │
                    │   - Users & Sessions      │
                    │   - Permissions & Logs    │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │   Tapo P100/P105/P110     │
                    │   Smart Plugs (LAN)       │
                    └───────────────────────────┘
```

---

## 3 | 인프라 아키텍처

### 🏠 Synology NAS 배포 최적화

- **호스팅 환경**  
  - Synology DSM 7.x 이상
  - Docker Package 설치 필요
  - 최소 2GB RAM 권장

- **네트워크 구성**  
  - 내부망: `84/HTTP` 포트로 Nginx → FastAPI
  - 외부 접근: Synology Reverse Proxy → HTTPS
  - 방화벽: 84, 5011 포트 허용

- **SSL/HTTPS 처리**  
  - Synology Domain Certificate 사용
  - Let's Encrypt 자동 갱신
  - 컨테이너 내부는 HTTP만 처리

- **확장성**  
  - Docker Compose 기반 배포
  - 수평 확장 가능한 구조
  - 로드 밸런싱 지원

- **모니터링 & 로깅**  
  - Docker 로그 수집
  - Synology Log Center 연동
  - 실시간 상태 모니터링

---

## 4 | 사전 요구 사항

| 항목 | 최소 버전 | 권장 버전 |
|------|-----------|-----------|
| **Synology DSM** | 7.0+ | 7.2+ |
| **Docker Package** | 20.10+ | 24.0+ |
| **Docker Compose** | 2.0+ | 2.20+ |
| **메모리** | 1GB | 2GB+ |
| **저장공간** | 500MB | 1GB+ |

---

## 5 | 빠른 시작 (⏱ 5 분)

### 1️⃣ 환경 설정

```bash
# 프로젝트 클론
git clone https://github.com/your-org/tapo-control.git
cd tapo-control

# 환경 변수 설정
cp env.template .env
nano .env  # 아래 설정 참조
```

### 2️⃣ 핵심 설정 (.env)

```bash
# 필수 설정
SECRET_KEY=your-super-secret-key-here
TAPO_EMAIL=your-tapo-account@email.com
TAPO_PASSWORD=your-tapo-password
PLUGS={"집컴": "192.168.1.100", "서버": "192.168.1.101"}

# 관리자 계정
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-password

# 선택 설정
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
```

### 3️⃣ 배포 실행

```bash
# 개발 환경 (Adminer 포함)
./manage.sh dev start

# 프로덕션 환경
./manage.sh prod start
```

### 4️⃣ 접속 확인

```bash
# 내부 접속
http://your-nas-ip:84          # 웹 UI
http://your-nas-ip:84/docs     # API 문서
http://your-nas-ip:5011        # FastAPI 직접 접속

# 개발 환경 추가
http://your-nas-ip:8081        # 데이터베이스 관리 (Adminer)
```

---

## 6 | 핵심 환경 변수 (.env)

| 변수 | 설명 | 예시 | 필수 |
|------|------|------|------|
| `SECRET_KEY` | JWT 토큰 서명 키 | `abc123...` | ✅ |
| `TAPO_EMAIL` | Tapo 계정 이메일 | `user@email.com` | ✅ |
| `TAPO_PASSWORD` | Tapo 계정 비밀번호 | `password123` | ✅ |
| `PLUGS` | 플러그 설정 (JSON) | `{"집컴": "192.168.1.100"}` | ✅ |
| `ADMIN_USERNAME` | 관리자 사용자명 | `admin` | ✅ |
| `ADMIN_PASSWORD` | 관리자 비밀번호 | `secure123` | ✅ |
| `APP_ENV` | 실행 환경 | `production` | ❌ |
| `DEBUG` | 디버그 모드 | `false` | ❌ |
| `LOG_LEVEL` | 로그 레벨 | `INFO` | ❌ |
| `NGINX_HTTP_PORT` | Nginx 포트 | `84` | ❌ |
| `ADMINER_PORT` | Adminer 포트 | `8081` | ❌ |

---

## 7 | 프로젝트 구조

```
tapo-control/
│
├─ app/                          # FastAPI 애플리케이션
│   ├─ __init__.py
│   ├─ main.py                   # FastAPI 엔트리포인트
│   ├─ config.py                 # Pydantic 설정 관리
│   ├─ db.py                     # SQLite 데이터베이스
│   ├─ models.py                 # SQLAlchemy 모델
│   ├─ schemas.py                # Pydantic 스키마
│   ├─ dependencies.py           # FastAPI 의존성
│   ├─ exceptions.py             # 커스텀 예외 처리
│   │
│   ├─ routers/                  # API 라우터
│   │   ├─ __init__.py
│   │   ├─ auth.py               # 인증 API
│   │   ├─ health.py             # 헬스체크
│   │   ├─ plugs.py              # 플러그 제어 API
│   │   └─ ui.py                 # 웹 UI 라우터
│   │
│   ├─ services/                 # 비즈니스 로직
│   │   ├─ __init__.py
│   │   ├─ auth.py               # 인증 서비스
│   │   ├─ permissions.py        # 권한 관리
│   │   └─ pyp100.py             # Tapo 제어 서비스
│   │
│   ├─ static/                   # 정적 파일
│   │   ├─ css/
│   │   │   └─ bootstrap.min.css
│   │   └─ js/
│   │       ├─ admin.js          # 관리자 페이지 JS
│   │       ├─ dashboard.js      # 대시보드 JS
│   │       └─ login.js          # 로그인 JS
│   │
│   └─ templates/                # Jinja2 템플릿
│       ├─ base.html             # 기본 레이아웃
│       ├─ login.html            # 로그인 페이지
│       ├─ dashboard.html        # 메인 대시보드
│       ├─ admin.html            # 관리자 페이지
│       └─ user.html             # 사용자 정보 페이지
│
├─ data/                         # 데이터 저장소
├─ logs/                         # 애플리케이션 로그
│
├─ nginx/                        # Nginx 설정
│   └─ nginx.conf                # 리버스 프록시 설정
│
├─ tests/                        # 테스트 스위트
│   ├─ __init__.py
│   ├─ test_auth.py              # 인증 테스트
│   └─ test_health.py            # 헬스체크 테스트
│
├─ create_admin.py               # 관리자 계정 생성 CLI
├─ create_user.py                # 사용자 계정 생성 CLI
├─ migrate_db.py                 # 데이터베이스 마이그레이션
├─ manage.sh                     # 배포 관리 스크립트
├─ manage.ps1                    # PowerShell 관리 스크립트
├─ Dockerfile                    # Python 3.12 + Uvicorn
├─ docker-compose.yml            # Docker Compose 구성
├─ requirements.txt              # Python 의존성
└─ env.template                  # 환경 변수 템플릿
```

---

## 8 | 사용자 관리

### 🔐 관리자 계정 생성

```bash
# 컨테이너 내부에서 실행
docker-compose exec web python /app/create_admin.py

# 또는 직접 실행
python create_admin.py
```

### 👤 일반 사용자 생성

```bash
# 컨테이너 내부에서 실행
docker-compose exec web python /app/create_user.py

# 또는 직접 실행
python create_user.py
```

### 🔑 권한 관리

| 역할 | 권한 | 설명 |
|------|------|------|
| **Admin** | 모든 플러그 접근 | 전체 시스템 관리 |
| **User** | 할당된 플러그만 | 제한된 접근 권한 |

### 📊 사용자별 플러그 권한

```bash
# 관리자 페이지에서 설정
http://your-nas-ip:84/admin

# 또는 API로 직접 설정
POST /admin/users/{user_id}/permissions
{
  "plug_name": "집컴",
  "grant": true
}
```

---

## 9 | 주요 API

### 🔐 인증 API

| 메서드 | 엔드포인트 | 설명 | 인증 |
|--------|------------|------|------|
| `POST` | `/auth/login` | JWT 토큰 발급 | ❌ |
| `POST` | `/auth/logout` | 로그아웃 | ✅ |
| `GET` | `/auth/me` | 현재 사용자 정보 | ✅ |

### 🔌 플러그 제어 API

| 메서드 | 엔드포인트 | 설명 | 인증 |
|--------|------------|------|------|
| `GET` | `/plugs/` | 플러그 목록 조회 | ✅ |
| `POST` | `/plugs/{name}/on` | 플러그 사용 예약 및 ON | ✅ |
| `POST` | `/plugs/{name}/off` | 플러그 예약 해제 및 OFF | ✅ |
| `GET` | `/plugs/{name}/status` | 플러그 상태 조회 | ✅ |
| `DELETE` | `/plugs/{name}/sessions` | 모든 세션 초기화 (Admin) | ✅ |

### 🏥 시스템 API

| 메서드 | 엔드포인트 | 설명 | 인증 |
|--------|------------|------|------|
| `GET` | `/healthz` | 헬스 체크 | ❌ |
| `GET` | `/docs` | Swagger UI | ❌ |

### 📝 API 응답 예시

```json
// 플러그 목록 조회
GET /plugs/
{
  "plugs": [
    {
      "name": "집컴",
      "ip": "192.168.1.100",
      "status": true,
      "active_users": 2,
      "users": ["admin", "user1"]
    }
  ]
}

// 플러그 상태 조회
GET /plugs/집컴/status
{
  "name": "집컴",
  "status": true,
  "active_users": 2,
  "users": ["admin", "user1"]
}
```

---

## 10 | 웹 UI 가이드

### 🖥️ 메인 대시보드 (`/`)

- **플러그 상태 표시**: 실시간 On/Off 상태
- **사용자 목록**: 현재 플러그를 사용 중인 사용자
- **제어 버튼**: 원클릭 On/Off 제어
- **권한 표시**: 접근 가능한 플러그만 표시

### 👤 사용자 페이지 (`/user`)

- **개인 정보**: 사용자명, 역할, 생성일
- **권한 목록**: 접근 가능한 플러그 목록
- **사용 이력**: 플러그 사용 기록

### 🔧 관리자 페이지 (`/admin`)

- **사용자 관리**: 전체 사용자 목록 및 권한 관리
- **플러그 관리**: 플러그 설정 및 상태 모니터링
- **시스템 정보**: 로그 및 성능 정보

### 🔐 로그인 페이지 (`/login`)

- **JWT 인증**: 토큰 기반 로그인
- **자동 리다이렉트**: 인증 후 대시보드로 이동
- **에러 처리**: 로그인 실패 시 메시지 표시

---

## 11 | 문제 해결 FAQ

### 🔧 일반적인 문제

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| **로그인 후 다시 로그인 페이지** | JWT 토큰 만료 | 재로그인 또는 토큰 갱신 |
| **401 Unauthorized** | 권한 없음 | 관리자에게 권한 요청 |
| **502 Bad Gateway** | 서비스 중단 | `./manage.sh prod restart` |
| **플러그 제어 실패** | 네트워크 연결 문제 | IP 주소 및 LAN 연결 확인 |

### 📋 로그 확인

```bash
# 전체 로그 확인
./manage.sh prod logs

# 특정 서비스 로그
docker-compose logs -f web
docker-compose logs -f nginx

# 실시간 로그 모니터링
tail -f logs/app.log
```

### 🔍 디버깅 명령어

```bash
# 컨테이너 상태 확인
docker-compose ps

# 데이터베이스 확인 (개발 환경)
http://your-nas-ip:8081

# API 상태 확인
curl http://your-nas-ip:5011/healthz

# 환경 변수 확인
docker-compose exec web env | grep -E "(SECRET|TAPO|PLUGS)"
```

### 🚨 긴급 복구

```bash
# 완전 재시작
./manage.sh prod stop
./manage.sh prod start

# 데이터베이스 초기화 (주의!)
rm users.db
./manage.sh prod restart

# 이미지 재빌드
./manage.sh prod build
```

---

## 12 | 로드맵

### 🎯 v1.0 계획 (2025년 Q2)

| 기능 | 상태 | 설명 |
|------|------|------|
| **PostgreSQL 마이그레이션** | 🛠️ 진행중 | SQLite → PostgreSQL |
| **Gunicorn Workers** | 📋 계획 | Uvicorn → Gunicorn |
| **Redis 캐싱** | 📋 계획 | 세션 및 상태 캐싱 |
| **WebSocket 실시간 업데이트** | 📋 계획 | 실시간 상태 동기화 |
| **Discord 알림** | 📋 계획 | 플러그 상태 변경 알림 |
| **백업 시스템** | 📋 계획 | 자동 데이터 백업 |

### 🔮 장기 계획

| 영역 | 기능 | 우선순위 |
|------|------|----------|
| **모니터링** | Prometheus + Grafana | 높음 |
| **로깅** | ELK 스택 연동 | 중간 |
| **보안** | OAuth2 + LDAP | 높음 |
| **확장성** | Kubernetes 배포 | 낮음 |
| **UI/UX** | React SPA 전환 | 중간 |

---

## 📞 지원 및 문의

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **Wiki**: 상세한 설정 가이드
- **Discussions**: 커뮤니티 토론

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

*마지막 업데이트: 2025년 1월 27일*
