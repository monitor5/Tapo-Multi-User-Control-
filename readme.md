# Tapo Control 시스템 사용자 매뉴얼 (Sprint 1 MVP)

> **버전** 0.2 – 2025-05-02  
> **대상** : DevOps · 내부 유저.

---

## 1. 개요

TP-Link Tapo 스마트 플러그를 원격으로 제어해 워크스테이션의 전원을 관리하는 **경량 FastAPI** 애플리케이션입니다.

- **주요 기능**  
  1. JWT 로그인 / 토큰 발급  
  2. 단일 플러그 제어 REST API  
  3. Bootstrap 기반 SSR 웹 UI  
  4. PyTest 단위 테스트  
  5. Docker Compose 배포

---

## 2. 시스템 아키텍처

```
┌──────────────┐      HTTP/HTTPS      ┌──────────────┐
│   Browser    │  ───────────────▶   │    Nginx     │
└──────────────┘  static / api / ui   └─────┬────────┘
                                             │ proxy_pass (현재 구현 잘 안되 있음. 개선 필요)
┌──────────────┐  5005/tcp    ┌──────────────┐
│  FastAPI     │◀────────────►│   Gunicorn   │
│  (Uvicorn)   │  internal    └──────────────┘
└──────┬───────┘
       │ TCP
┌──────▼───────┐
│   Tapo P100  │  (LAN IP) - turn_on/off/status
└──────────────┘
```

---

## 3. 요구 사항

| 항목 | 최소 버전 |
|------|-----------|
| Docker | 20.10+ |
| docker-compose | v2.20+ |
| (개발용) Python | 3.12 |

---

## 4. 빠른 시작 (3 분)

```bash
git clone https://github.com/your-org/tapo-control.git
cd tapo-control

# 1) 환경 변수 설정
cp .env.example .env           # 기본 샘플
# └─ ADMIN_PASSWORD_HASH 값 생성:  python -m passlib.hash bcrypt -g

# 2) 빌드·기동
docker compose up -d --build   # 최초 1회
# (수정 후) docker compose down && docker compose up -d --build
```

### 기본 접속 포트  

| 서비스 | URL |
|--------|-----|
| Nginx Reverse Proxy | http://localhost |
| Swagger (자동 문서) | http://localhost/docs |
| Redoc | http://localhost/redoc |

---

## 5. 환경 변수 참조(.env)

| 변수 | 설명 | 예시 |
|------|------|------|
| **ADMIN_USERNAME** | 정적 관리자 ID | `admin` |
| **ADMIN_PASSWORD_HASH** | bcrypt 해시 | `$2b$12$…` |
| **JWT_SECRET** | 토큰 서명 키 | `supersecretjwtkey` |
| **JWT_ALGORITHM** | 알고리즘 | `HS256` |
| **HOST / PORT** | FastAPI 내부 바인딩 | `0.0.0.0` / `5005` |
| **LOG_LEVEL** | 로그 레벨 | `INFO` |
| **TAPO_PLUGS** | `이름=IP` 다중 콤마 | `pc01=192.168.1.31,pc02=192.168.1.32` |

> **참고** : `.env.example` 파일을 열어 모든 옵션을 확인하세요.

---

## 6. 디렉터리 레이아웃

```
app/
 ├─ main.py            # FastAPI 진입점
 ├─ routers/           # health, auth, plugs
 ├─ services/          # pyp100_service
 ├─ templates/         # Jinja2 UI (base, login, dashboard)
 ├─ static/            # css, js
 ├─ .env               # settings 참조. ( ip, ,username , password) 
 └─ config.py          # Pydantic-Settings
docker-compose.yml
Dockerfile
tests/                 # pytest 스위트
```

---

## 7. 사용자 추가 (generated bcrypt hash)

1. 쉘에서 비밀번호 해시 생성  
   ```bash
docker exec -it tapo-control-web python /app/create_user.py
[user_name]
[user_password]
   ```
2. `.env` 파일의 `ADMIN_PASSWORD_HASH=` 값에 붙여넣기  
3. 컨테이너 재배포(`docker compose up -d --build`)  

> **여러 계정**이 필요하면 Sprint 2에서 **SQLite 사용자 테이블**로 전환하세요.

---

## 8. API 참고 (예시 Curl)

```bash
# A. 로그인 → JWT
TOKEN=$(curl -sf \
  -F "username=admin" \
  -F "password=비밀번호" \
  http://localhost/auth/login | jq -r .access_token)

# B. 플러그 목록
curl -H "Authorization: Bearer $TOKEN" http://localhost/plugs/

# C. 전원 켜기
curl -X POST -H "Authorization: Bearer $TOKEN" \
     http://localhost/plugs/pc01/on
```

| 메서드 | 경로 | 설명 | 응답 코드 |
|--------|------|------|-----------|
| `GET`  | `/healthz` | 헬스체크 | 200 | ( fastapi 백이 살아있는지만 파악가능 )
| `POST` | `/auth/login` | JWT 발급 | 200 / 401 |
| `GET`  | `/plugs/` | 플러그 리스트 | 200 |
| `POST` | `/plugs/{name}/on` | 전원 ON | 200 / 404 |
| `POST` | `/plugs/{name}/off` | 전원 OFF | 200 / 404 |
| `GET`  | `/plugs/{name}/status` | 상태 | 200 / 404 |

---

## 9. 웹 UI 사용 흐름

1. **`/login`** 접속  
   - ID·PW 입력 → 내부 API(`/auth/login`) 호출  
   - 성공 시 `localStorage.tapo_jwt` 에 토큰 저장 → `/` 리다이렉트
2. **대시보드 (`/`)**  
   - JS(`dashboard.js`) 가 `/plugs/` 호출 → 테이블 생성  
   - **켜기/끄기** 버튼 클릭 → `/plugs/{name}/on|off` 호출 후 테이블 리로드
3. **로그아웃** 버튼 → 토큰 삭제 후 `/login`

> **모바일 뷰**도 Bootstrap 5 기본 반응형으로 동작합니다.

---

## 10. 테스트 스위트

```bash
docker compose exec web pytest -q
```

- `tests/test_auth.py` : JWT 로그인 성공/실패, 보호 엔드포인트 401  
- `tests/test_plugs.py` : 켜기/끄기/상태, 404 처리

---

## 11. 문제해결 가이드

| 증상 | 확인 포인트 |
|------|------------|
| 401 Unauthorized | 토큰 만료?  `localStorage` 삭제 후 재로그인 |
| 502 (Nginx) | `docker compose ps` 로 web 컨테이너 정상 여부 |
| 플러그 안 켜짐 | `TAPO_PLUGS` IP 오타, 기기 오프라인 |
| bcrypt 검증 실패 | 해시 붙여넣기 시 공백 포함 여부 |

**로그 경로**

```bash
docker compose logs -f web   # FastAPI/Gunicorn
docker compose logs -f nginx # Reverse Proxy
```

---

## 12. 확장 로드맵 (예고)

| Sprint | 기능 |
|--------|------|
| 2 | **여러 플러그 동시 제어**, Discord 알림, APScheduler 예약 | done
| 3 | SQLite 사용자 DB → Postgres 마이그레이션, 역할별 권한 | 진행중.
| 4 | 보안 개선. https, 로그인 관리 시스템 역할별 권한 고도화. | 
| 4 | Prometheus 메트릭 + Grafana 대시보드, 다중 사이트 지원 | 진행 안할예정. Prometheus 필요없이 잘 구동될 것으로 보임. ( 소규모 이용자 그룹 )

---

### 문의

- Slack : `없지롱`  
- Email : 000@office.kw.ac.kr
