from fastapi.security import OAuth2PasswordBearer

# OAuth2 인증 스키마 정의
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") 