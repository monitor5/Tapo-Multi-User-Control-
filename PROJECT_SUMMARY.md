# 🔌 Tapo Control - 프로젝트 요약

## 📖 프로젝트 개요

**Tapo Control**은 TP-Link Tapo 스마트 플러그를 웹에서 관리하는 시스템입니다.

### ✨ 핵심 기능
- 🔌 **스마트 플러그 제어**: Tapo P100/P105/P110 ON/OFF 제어
- 👥 **다중 사용자 지원**: 여러 사용자가 동시에 플러그 사용 가능
- 🔐 **권한 관리**: 사용자별 플러그 접근 권한 설정
- 🌐 **웹 인터페이스**: 반응형 웹 UI
- 🐳 **Docker 배포**: 컨테이너 기반 배포
- 🏠 **Synology 최적화**: NAS 환경에서 HTTPS 지원

## 🛠 기술 스택

| 분야 | 기술 |
|------|------|
| **백엔드** | FastAPI, SQLAlchemy, SQLite, JWT |
| **프론트엔드** | Bootstrap 5, Vanilla JavaScript, Jinja2 |
| **인프라** | Docker, Nginx, Synology DSM |
| **IoT** | plugp100 라이브러리 |

## 🏗 아키텍처

```
사용자 → HTTPS:443 → Synology 프록시 → HTTP:84 → Nginx → FastAPI:5011 → Tapo 플러그
```

## 📊 데이터베이스

| 테이블 | 설명 |
|--------|------|
| **Users** | 사용자 정보 (id, username, password, role) |
| **Plugs** | 플러그 정보 (name, ip) |
| **PlugSessions** | 플러그 사용 세션 |
| **UserPlugPermissions** | 사용자별 플러그 접근 권한 |

## 🚀 빠른 시작

1. **환경 설정**
   ```bash
   cp env.template .env
   nano .env  # 설정 편집
   ```

2. **실행**
   ```bash
   ./manage.sh prod start
   ```

3. **접속**
   - 웹: http://localhost:84
   - API 문서: http://localhost:84/docs

## 🔑 주요 API

| 엔드포인트 | 설명 |
|------------|------|
| `POST /auth/login` | 로그인 |
| `GET /plugs/` | 플러그 목록 |
| `POST /plugs/{name}/on` | 플러그 ON |
| `POST /plugs/{name}/off` | 플러그 OFF |
| `GET /admin` | 관리자 페이지 |

## 👤 사용자 역할

- **관리자 (admin)**: 모든 플러그 접근 + 사용자 관리
- **사용자 (user)**: 권한이 부여된 플러그만 접근

## 🌟 특별한 기능

### 스마트 세션 관리
- 여러 사용자가 동시에 같은 플러그 사용 가능
- 마지막 사용자가 나가면 자동으로 플러그 OFF
- 실시간 사용자 목록 표시

### 권한 시스템
- 사용자별로 특정 플러그만 접근 가능
- 관리자 페이지에서 실시간 권한 관리
- 권한 매트릭스 뷰 제공

## 📁 파일 구조

```
tapo-control/
├── app/                    # 메인 애플리케이션
│   ├── routers/           # API 라우터
│   ├── services/          # 비즈니스 로직
│   ├── templates/         # 웹 템플릿
│   └── static/            # 정적 파일
├── docker-compose.yml     # Docker 설정
├── env.template          # 환경변수 템플릿
├── manage.sh            # 관리 스크립트
└── requirements.txt     # Python 의존성
```

## 🎯 주요 화면

1. **대시보드**: 플러그 목록 및 제어
2. **관리자 페이지**: 사용자 관리, 권한 설정
3. **로그인 페이지**: JWT 토큰 기반 인증

## 🔧 관리 명령

```bash
# 개발 환경
./manage.sh dev start
./manage.sh dev logs

# 운영 환경
./manage.sh prod start
./manage.sh prod stop

# 사용자 관리
python create_admin.py
python create_user.py

# 데이터베이스
python migrate_db.py
```

## 📋 환경 변수 (필수)

```env
SECRET_KEY=your-jwt-secret-key
TAPO_EMAIL=your-tapo-account@email.com
TAPO_PASSWORD=your-tapo-password
PLUGS={"집컴": "192.168.45.179"}
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-password
```

## 🚨 중요 사항

- **보안**: JWT 시크릿 키는 반드시 변경
- **네트워크**: 플러그와 같은 네트워크에 있어야 함
- **권한**: 첫 실행 시 관리자 계정 자동 생성
- **SSL**: Synology DSM에서 HTTPS 인증서 관리

## 📚 문서

- 📘 **상세 문서**: [DOCUMENTATION.md](DOCUMENTATION.md)
- 📗 **설치 가이드**: [readme.md](readme.md)
- 🔧 **개발 가이드**: 문서 내 개발 섹션 참조

---

**빠른 도움말**: 문제가 있으면 `./manage.sh dev logs`로 로그 확인 