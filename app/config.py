from typing import Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import logging
import os

logger = logging.getLogger(__name__)

class PlugConfig(BaseModel):
    name: str
    ip: str


class Settings(BaseSettings):
    # ─── App ───────────────────────────────────────────────
    APP_ENV: str = Field("development", env="APP_ENV")
    DEBUG: bool = Field(True, env="DEBUG")
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(5005, env="PORT")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    # ─── JWT ───────────────────────────────────────────────
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # ─── Tapo ──────────────────────────────────────────────
    TAPO_EMAIL: str = Field(..., env="TAPO_EMAIL")
    TAPO_PASSWORD: str = Field(..., env="TAPO_PASSWORD")
    PLUGS_RAW: str = Field("", env="PLUGS")
    
    @property
    def PLUGS(self) -> List[PlugConfig]:
        """
        환경변수 PLUGS를 파싱하여 PlugConfig 객체 리스트로 변환
        지원하는 형식:
        1. JSON 형식 - 딕셔너리: {"plug1": "192.168.1.100", "plug2": "192.168.1.101"}
        """
        try:
            # 직접 환경변수 가져오기 
            env_plugs = os.environ.get('PLUGS', '')
            
            if not env_plugs:
                logger.error("환경변수 PLUGS가 비어있습니다")
                return []
                
            logger.info(f"환경변수 PLUGS 값: '{env_plugs}'")
            
            # JSON 파싱 (큰따옴표 누락된 경우 대응)
            try:
                # 제대로 된 JSON으로 먼저 시도
                data = json.loads(env_plugs)
                logger.info(f"정상 JSON 파싱 성공: {data}")
            except json.JSONDecodeError:
                # 큰따옴표 없는 JSON인 경우 (ex: {key:value})
                try:
                    # 1) 작은따옴표를 큰따옴표로 변환
                    fixed = env_plugs.replace("'", '"')
                    # 2) 키에 큰따옴표 추가 - {key:value} -> {"key":"value"}
                    import re
                    fixed = re.sub(r'([{,])\s*([^"\s{}:,]+)\s*:', r'\1"\2":', fixed)
                    # 3) 값에 큰따옴표 추가 (숫자나 객체가 아닌 경우만)
                    fixed = re.sub(r':\s*([^"\d{}\s\[\],]+)([,}])', r':"\1"\2', fixed)
                    logger.info(f"수정된 JSON: {fixed}")
                    data = json.loads(fixed)
                    logger.info(f"수정된 JSON 파싱 성공: {data}")
                except Exception as e:
                    logger.error(f"수정된 JSON 파싱 실패: {str(e)}")
                    # 3) 최종 대안: 하드코딩된 값 사용
                    logger.warning("하드코딩된 값으로 폴백")
                    data = {"집컴": "192.168.45.179", "fakeplug": "192.168.0.1"}
            
            if not isinstance(data, dict):
                logger.error(f"PLUGS 환경변수는 딕셔너리 형태여야 합니다: {type(data)}")
                return []
                
            # 딕셔너리를 PlugConfig 객체 리스트로 변환
            result = [PlugConfig(name=name, ip=ip) for name, ip in data.items()]
            logger.info(f"플러그 설정 {len(result)}개 로드됨: {result}")
            return result
            
        except Exception as e:
            logger.error(f"PLUGS 파싱 중 예외 발생: {str(e)}")
            return []

    model_config = SettingsConfigDict(case_sensitive=True)


settings = Settings()
