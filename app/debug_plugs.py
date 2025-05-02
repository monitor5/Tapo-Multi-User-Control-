import os
import logging
import json
from pydantic import BaseModel
from typing import List

# 로그 레벨 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PlugConfig(BaseModel):
    name: str
    ip: str

# 환경변수 직접 확인
env_plugs = os.environ.get('PLUGS', '없음')
print(f"환경변수 PLUGS 직접 확인: '{env_plugs}'")

# .env 파일 확인
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('PLUGS='):
                print(f".env 파일의 PLUGS: {line.strip()}")
except Exception as e:
    print(f".env 파일 확인 중 오류: {e}")

# JSON 파싱 시도
if env_plugs and env_plugs != '없음':
    try:
        if env_plugs.startswith('{') or env_plugs.startswith('['):
            data = json.loads(env_plugs)
            print(f"JSON 파싱 결과: {data}")
            
            if isinstance(data, dict):
                plugs = [PlugConfig(name=name, ip=ip) for name, ip in data.items()]
                print(f"딕셔너리에서 변환된 플러그: {plugs}")
    except Exception as e:
        print(f"JSON 파싱 오류: {e}")

print("디버그 스크립트 완료") 