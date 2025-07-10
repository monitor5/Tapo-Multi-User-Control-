# 🔌 Tapo Control - 스마트 플러그 관리 시스템

**Tapo Control**은 TP-Link Tapo 스마트 플러그(P100/P105/P110)를 웹 브라우저에서 관리할 수 있는 종합적인 시스템입니다. 다중 사용자 지원, 권한 관리, 세션 기반 플러그 제어 등의 기능을 제공합니다.

## 📋 목차

1. [프로젝트 개요](#-프로젝트-개요)
2. [기술 스택](#-기술-스택)
3. [시스템 아키텍처](#-시스템-아키텍처)
4. [설치 및 실행](#-설치-및-실행)
5. [데이터베이스 구조](#-데이터베이스-구조)
6. [API 명세](#-api-명세)
7. [프론트엔드 구성](#-프론트엔드-구성)
8. [인증 및 권한](#-인증-및-권한)
9. [배포 및 운영](#-배포-및-운영)
10. [개발 가이드](#-개발-가이드)

## 🎯 프로젝트 개요

### 주요 기능

- **스마트 플러그 제어**: Tapo P100/P105/P110 플러그의 ON/OFF 제어
- **다중 사용자 지원**: 여러 사용자가 동시에 플러그를 사용할 수 있는 세션 관리
- **권한 관리**: 사용자별로 특정 플러그에 대한 접근 권한 설정
- **역할 기반 접근 제어**: 관리자와 일반 사용자 구분
- **실시간 상태 확인**: 플러그의 현재 상태 및 사용 중인 사용자 목록 표시
- **웹 인터페이스**: 반응형 웹 UI를 통한 직관적인 제어

### 핵심 특징

- **세션 기반 제어**: 플러그를 사용하는 사용자가 있는 한 ON 상태 유지
- **스마트 OFF 제어**: 마지막 사용자가 나가면 자동으로 플러그 OFF
- **Synology NAS 최적화**: Synology 환경에서의 HTTPS 배포 지원
- **Docker 컨테이너화**: 간편한 배포 및 관리

## 🛠 기술 스택

### 백엔드
- **FastAPI**: 고성능 Python 웹 프레임워크
- **SQLAlchemy**: ORM 및 데이터베이스 추상화
- **SQLite**: 경량 데이터베이스 (PostgreSQL 전환 가능)
- **plugp100**: Tapo 플러그 제어 라이브러리
- **JWT**: 토큰 기반 인증
- **Pydantic**: 데이터 검증 및 설정 관리

### 프론트엔드
- **Bootstrap 5**: 반응형 UI 프레임워크
- **Vanilla JavaScript**: 클라이언트 사이드 로직
- **Jinja2**: 서버 사이드 템플릿 엔진
- **Bootstrap Icons**: 아이콘 세트

### 인프라 및 배포
- **Docker**: 컨테이너화
- **Nginx**: 리버스 프록시
- **Synology DSM**: HTTPS 터미네이션
- **Adminer**: 개발용 데이터베이스 관리

## 🏗 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    Synology NAS                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Reverse Proxy                          │ │
│  │         (HTTPS Termination)                         │ │
│  │              Port 443                               │ │
│  └─────────────────────────────────────────────────────┘ │
│                          │                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Nginx Container                        │ │
│  │                Port 84                              │ │
│  └─────────────────────────────────────────────────────┘ │
│                          │                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │           FastAPI Application                       │ │
│  │               Port 5011                             │ │
│  │  ┌─────────────────────────────────────────────────┐ │ │
│  │  │              Routes                             │ │ │
│  │  │  • /auth    - Authentication                    │ │ │
│  │  │  • /plugs   - Plug Control                      │ │ │
│  │  │  • /        - Web UI                            │ │ │
│  │  │  • /admin   - Admin Panel                       │ │ │
│  │  └─────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────┐ │ │
│  │  │            Services                             │ │ │
│  │  │  • AuthService   - JWT Authentication           │ │ │
│  │  │  • Pyp100Service - Tapo Communication          │ │ │
│  │  │  • PermissionService - Access Control          │ │ │
│  │  └─────────────────────────────────────────────────┘ │ │
│  │  ┌─────────────────────────────────────────────────┐ │ │
│  │  │            Database                             │ │ │
│  │  │  • Users                                        │ │ │
│  │  │  • Plugs                                        │ │ │
│  │  │  • PlugSessions                                 │ │ │
│  │  │  • UserPlugPermissions                          │ │ │
│  │  └─────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          │ IP Network
                          │
              ┌─────────────────────────┐
              │     Tapo Smart Plugs    │
              │  P100 / P105 / P110     │
              └─────────────────────────┘
```

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# 프로젝트 클론
git clone <repository-url>
cd tapo-control

# 환경 변수 설정
cp env.template .env
nano .env  # 환경 변수 편집
```

### 2. 환경 변수 설정 (.env)

```env
# 앱 설정
APP_ENV=development
DEBUG=true
PORT=5011

# 보안 설정
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Tapo 계정 정보
TAPO_EMAIL=your-tapo-account@email.com
TAPO_PASSWORD=your-tapo-password

# 플러그 설정 (JSON 형식)
PLUGS={"집컴": "192.168.45.179", "거실TV": "192.168.45.180"}

# 관리자 계정
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-password

# 포트 설정
NGINX_HTTP_PORT=84
ADMINER_PORT=8081
```

### 3. 실행 방법

**개발 환경:**
```bash
./manage.sh dev start
# 또는 PowerShell에서: .\manage.ps1 dev start
```

**운영 환경:**
```bash
./manage.sh prod start
# 또는 PowerShell에서: .\manage.ps1 prod start
```

### 4. 접속 URL

- **웹 애플리케이션**: http://localhost:84
- **API 문서**: http://localhost:84/docs
- **데이터베이스 관리** (개발 시): http://localhost:8081
- **FastAPI 직접 접속**: http://localhost:5011

## 🗄 데이터베이스 구조

### ERD (Entity Relationship Diagram)

```
┌─────────────────┐       ┌─────────────────┐
│      User       │       │      Plug       │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ name (PK)       │
│ username        │       │ ip              │
│ hashed_password │       │                 │
│ role            │       │                 │
└─────────────────┘       └─────────────────┘
         │                         │
         │                         │
         │ 1:N                     │ 1:N
         │                         │
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│  PlugSession    │       │UserPlugPermission│
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ plug_name (FK)  │       │ user_id (FK)    │
│ user_id (FK)    │       │ plug_name (FK)  │
│ started_at      │       │ created_at      │
└─────────────────┘       └─────────────────┘
```

### 테이블 상세

#### Users 테이블
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(100) NOT NULL,
    role VARCHAR(10) DEFAULT 'user'
);
```

#### Plugs 테이블
```sql
CREATE TABLE plugs (
    name VARCHAR(50) PRIMARY KEY,
    ip VARCHAR(50) NOT NULL
);
```

#### PlugSessions 테이블
```sql
CREATE TABLE plug_sessions (
    id INTEGER PRIMARY KEY,
    plug_name VARCHAR(50) NOT NULL,
    user_id INTEGER NOT NULL,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plug_name) REFERENCES plugs(name),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### UserPlugPermissions 테이블
```sql
CREATE TABLE user_plug_permissions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    plug_name VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (plug_name) REFERENCES plugs(name)
);
```

## 🔌 API 명세

### 인증 API (`/auth`)

#### POST /auth/login
- **설명**: 사용자 로그인 및 JWT 토큰 발급
- **요청**: 
  ```json
  {
    "username": "admin",
    "password": "password"
  }
  ```
- **응답**: 
  ```json
  {
    "access_token": "jwt_token_here",
    "token_type": "bearer",
    "expires_in": 3600
  }
  ```

#### POST /auth/logout
- **설명**: 로그아웃 (클라이언트 측 토큰 삭제)
- **헤더**: `Authorization: Bearer <token>`

### 관리자 API (`/auth/admin`)

#### POST /auth/admin/users
- **설명**: 새 사용자 생성 (관리자 전용)
- **요청**:
  ```json
  {
    "username": "newuser",
    "password": "password123",
    "role": "user"
  }
  ```

#### GET /auth/admin/users
- **설명**: 사용자 목록 조회 (관리자 전용)
- **응답**:
  ```json
  {
    "users": [
      {
        "id": 1,
        "username": "admin",
        "role": "admin"
      }
    ]
  }
  ```

#### GET /auth/admin/users/permissions
- **설명**: 사용자별 플러그 권한 조회
- **응답**:
  ```json
  {
    "users": [
      {
        "id": 1,
        "username": "user1",
        "role": "user",
        "allowed_plugs": ["집컴", "거실TV"]
      }
    ]
  }
  ```

#### POST /auth/admin/permissions/grant
- **설명**: 플러그 권한 부여
- **요청**:
  ```json
  {
    "user_id": 1,
    "plug_name": "집컴"
  }
  ```

#### DELETE /auth/admin/permissions/revoke
- **설명**: 플러그 권한 회수
- **요청**:
  ```json
  {
    "user_id": 1,
    "plug_name": "집컴"
  }
  ```

### 플러그 제어 API (`/plugs`)

#### GET /plugs/
- **설명**: 사용자가 접근 가능한 플러그 목록 조회
- **응답**:
  ```json
  [
    {
      "name": "집컴",
      "ip": "192.168.45.179",
      "status": true,
      "active_users": 2,
      "users": ["user1", "user2"]
    }
  ]
  ```

#### POST /plugs/{name}/on
- **설명**: 플러그 사용 시작 (ON)
- **응답**:
  ```json
  {
    "name": "집컴",
    "status": true,
    "active_users": 1,
    "users": ["user1"]
  }
  ```

#### POST /plugs/{name}/off
- **설명**: 플러그 사용 종료 (OFF, 마지막 사용자인 경우)
- **응답**:
  ```json
  {
    "name": "집컴",
    "status": false,
    "active_users": 0,
    "users": []
  }
  ```

#### GET /plugs/{name}/status
- **설명**: 플러그 상태 조회
- **응답**:
  ```json
  {
    "name": "집컴",
    "status": true,
    "active_users": 1,
    "users": ["user1"]
  }
  ```

### 웹 UI 라우트

#### GET /
- **설명**: 메인 대시보드 페이지
- **인증**: 필요

#### GET /login
- **설명**: 로그인 페이지
- **인증**: 불필요

#### GET /admin
- **설명**: 관리자 페이지
- **인증**: 관리자 권한 필요

#### GET /user
- **설명**: 사용자 정보 페이지
- **인증**: 필요

## 🎨 프론트엔드 구성

### 페이지 구조

```
app/templates/
├── base.html          # 기본 레이아웃
├── login.html         # 로그인 페이지
├── dashboard.html     # 메인 대시보드
├── admin.html         # 관리자 페이지
└── user.html          # 사용자 정보 페이지

app/static/
├── css/
│   └── bootstrap.min.css
└── js/
    ├── login.js       # 로그인 로직
    ├── dashboard.js   # 대시보드 로직
    └── admin.js       # 관리자 페이지 로직
```

### 주요 기능

#### 대시보드 (dashboard.html)
- **플러그 목록**: 권한이 있는 플러그만 표시
- **실시간 상태**: 플러그 ON/OFF 상태 및 사용자 수
- **제어 버튼**: 
  - "사용" 버튼: 플러그 ON 및 세션 생성
  - "나가기" 버튼: 세션 종료 (마지막 사용자면 플러그 OFF)
- **스마트 버튼 상태**: 
  - 사용 중이면 "사용" 버튼 비활성화
  - 사용 중이 아니면 "나가기" 버튼 비활성화

#### 관리자 페이지 (admin.html)
- **사용자 관리**: 생성, 삭제, 비밀번호 재설정
- **권한 관리**: 사용자별 플러그 접근 권한 설정
- **권한 매트릭스**: 사용자-플러그 권한 테이블 뷰
- **실시간 업데이트**: 권한 변경 시 즉시 반영

#### 사용자 정보 페이지 (user.html)
- **프로필 정보**: 사용자명, 권한 레벨 표시
- **권한 안내**: 관리자인 경우 추가 권한 안내

### JavaScript 모듈

#### dashboard.js
```javascript
// 주요 기능
- 플러그 목록 로드 및 렌더링
- 플러그 ON/OFF 제어
- 실시간 상태 업데이트
- 토큰 기반 인증 관리
- 에러 처리 및 사용자 피드백
```

#### admin.js
```javascript
// 주요 기능
- 사용자 생성/삭제
- 비밀번호 재설정
- 권한 매트릭스 관리
- 실시간 권한 업데이트
- 모달 기반 UI 제어
```

## 🔐 인증 및 권한

### 인증 플로우

1. **로그인**: 사용자명/비밀번호로 JWT 토큰 발급
2. **토큰 저장**: 클라이언트에서 localStorage에 저장
3. **API 요청**: 모든 API 요청에 `Authorization: Bearer <token>` 헤더 포함
4. **토큰 검증**: 서버에서 JWT 토큰 검증 후 사용자 정보 추출

### 권한 시스템

#### 역할 기반 접근 제어 (RBAC)
- **admin**: 모든 플러그 접근 + 시스템 관리
- **user**: 권한이 부여된 플러그만 접근

#### 플러그 권한 관리
- **관리자**: 모든 플러그에 자동 접근 권한
- **일반 사용자**: 명시적으로 권한이 부여된 플러그만 접근
- **권한 부여/회수**: 관리자가 관리자 페이지에서 설정

### 보안 설정

#### JWT 토큰
```python
# 설정 예시
SECRET_KEY = "your-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
```

#### 비밀번호 해싱
```python
# bcrypt 사용
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

## 🚀 배포 및 운영

### Docker 컨테이너 구성

```yaml
# docker-compose.yml 주요 구성
services:
  web:                    # FastAPI 애플리케이션
    build: .
    ports:
      - "5011:5011"
    
  nginx:                  # 리버스 프록시
    image: nginx:alpine
    ports:
      - "84:80"
    
  adminer:                # 데이터베이스 관리 (개발용)
    image: adminer
    ports:
      - "8081:8080"
```

### Synology NAS 배포

#### 1. 포트 설정
- **FastAPI**: 5011 (내부 접근)
- **Nginx**: 84 (HTTP, Synology 리버스 프록시로 연결)
- **Adminer**: 8081 (개발용)

#### 2. HTTPS 설정
```
사용자 → HTTPS:443 → Synology 리버스 프록시 → HTTP:84 → Nginx → FastAPI:5011
```

#### 3. 배포 단계
```bash
# 1. 환경 설정
cp env.template .env
nano .env

# 2. 운영 환경 시작
./manage.sh prod start

# 3. Synology DSM에서 리버스 프록시 설정
# - 소스: HTTPS://your-domain.com:443
# - 대상: HTTP://localhost:84
```

### 관리 스크립트

#### manage.sh (Linux/macOS)
```bash
./manage.sh dev start      # 개발 환경 시작
./manage.sh prod start     # 운영 환경 시작
./manage.sh dev logs       # 로그 확인
./manage.sh prod stop      # 운영 환경 중지
```

#### manage.ps1 (Windows PowerShell)
```powershell
.\manage.ps1 dev start     # 개발 환경 시작
.\manage.ps1 prod start    # 운영 환경 시작
```

### 헬스 체크

```bash
# 애플리케이션 상태 확인
curl http://localhost:84/healthz

# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f
```

## 💻 개발 가이드

### 개발 환경 설정

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
cp env.template .env

# 3. 개발 서버 실행
./manage.sh dev start

# 4. 데이터베이스 초기화
python migrate_db.py
```

### 새로운 플러그 추가

1. **환경 변수 수정** (.env)
   ```env
   PLUGS={"기존플러그": "192.168.1.100", "새플러그": "192.168.1.101"}
   ```

2. **애플리케이션 재시작**
   ```bash
   ./manage.sh prod restart
   ```

3. **관리자 페이지에서 권한 설정**
   - 사용자별로 새 플러그 접근 권한 부여

### 새로운 사용자 추가

#### 방법 1: 웹 인터페이스 (권장)
1. 관리자 계정으로 로그인
2. 관리자 페이지 → 새 사용자 생성
3. 플러그 권한 설정

#### 방법 2: 명령줄 도구
```bash
# 일반 사용자 생성
python create_user.py

# 관리자 생성
python create_admin.py
```

### 데이터베이스 관리

#### 백업
```bash
# 데이터베이스 백업
cp users.db users.db.backup.$(date +%Y%m%d_%H%M%S)
```

#### 마이그레이션
```bash
# 스키마 업데이트
python migrate_db.py
```

#### 초기화
```bash
# 데이터베이스 초기화 (주의: 모든 데이터 삭제)
rm users.db
./manage.sh prod restart
```

### 로그 관리

#### 로그 위치
- **컨테이너 로그**: `docker-compose logs`
- **애플리케이션 로그**: `logs/` 디렉터리
- **Nginx 로그**: 컨테이너 내부 `/var/log/nginx/`

#### 로그 레벨 설정
```env
# .env 파일에서 설정
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### 테스트

```bash
# 테스트 실행
python -m pytest

# 특정 테스트 실행
python -m pytest tests/test_auth.py

# 커버리지 포함 테스트
python -m pytest --cov=app
```

### 개발 도구

#### API 문서
- **Swagger UI**: http://localhost:84/docs
- **ReDoc**: http://localhost:84/redoc

#### 데이터베이스 관리
- **Adminer**: http://localhost:8081 (개발 환경)

#### 로컬 Python 테스트
```bash
# 로컬 환경에서 Python 의존성 테스트
python test_local_python.py
```

## 📚 참고 자료

### 주요 라이브러리 문서
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [plugp100](https://github.com/petretiandrea/plugp100)
- [Bootstrap 5](https://getbootstrap.com/)

### 관련 기술 문서
- [JWT](https://jwt.io/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Nginx](https://nginx.org/en/docs/)
- [Synology DSM](https://www.synology.com/en-us/dsm)

### 트러블슈팅
- [문제 해결 가이드](readme.md#🚨-troubleshooting)
- [이슈 리포팅](https://github.com/your-repo/issues)

---

**최종 업데이트**: 2024년 12월
**버전**: 1.0.0
**문서 관리자**: 프로젝트 팀 