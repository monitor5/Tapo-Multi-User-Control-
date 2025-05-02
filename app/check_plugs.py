import logging
from app.config import settings
from app.services.pyp100 import pyp100_service

# 디버그 로그 활성화
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# PLUGS 환경변수 확인
print(f"PLUGS_RAW: '{settings.PLUGS_RAW}'")
print(f"PLUGS 객체: {list(settings.PLUGS)}")
print(f"pyp100_service.plugs: {pyp100_service.plugs}")

# 설정 완료되었는지 확인
if not pyp100_service.plugs:
    print("플러그 설정이 없습니다. 환경변수 PLUGS를 확인하세요.")
else:
    print(f"{len(pyp100_service.plugs)}개의 플러그가 설정되었습니다:") 