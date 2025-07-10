import logging
from fastapi import HTTPException, status
from plugp100.common.credentials import AuthCredential
from plugp100.new.device_factory import (
    connect,
    DeviceConnectConfiguration,
)
from typing import Dict, Any

from app.config import settings

logger = logging.getLogger(__name__)


class Pyp100Service:
    """
    비동기 Tapo P100 제어 서비스 (plugp100 v5.1.4).
    """

    def __init__(self):
        # 디버그 로그 추가
        logger.debug(f"PLUGS 설정 초기화 시작: raw={settings.PLUGS_RAW!r}")
        logger.debug(f"파싱된 PLUGS: {list(settings.PLUGS)}")
        
        # PlugConfig 리스트를 딕셔너리로 변환
        self._plugs: Dict[str, str] = {
            plug.name: plug.ip for plug in settings.PLUGS
        }
        
        logger.debug(f"최종 플러그 목록: {self._plugs}")
        
        if not self._plugs:
            logger.warning("유효한 플러그 설정이 없습니다. 환경변수 PLUGS를 확인하세요.")

    @property
    def plugs(self) -> Dict[str, str]:
        return self._plugs

    async def _connect(self, name: str):
        if name not in self._plugs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plug '{name}' not found"
            )
        ip = self._plugs[name]
        creds = AuthCredential(settings.TAPO_EMAIL, settings.TAPO_PASSWORD)
        cfg = DeviceConnectConfiguration(host=ip, port=81, credentials=creds)

        try:
            device = await connect(cfg)
            # 최초 상태 채우기
            await device.update()
            return device
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[Pyp100Service] connect/update '{name}' failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Cannot communicate with plug '{name}' ({ip}): {e}"
            )

    def _parse_state(self, raw: dict[str, Any]) -> bool:
        """
        raw_state 에서 on/off 를 판별.
         1) device_on (v5.1.4 firmware)
         2) top-level on
         3) system.get_sysinfo.relay_state
        """
        # 1) firmware v1.2.5+ uses device_on
        if "device_on" in raw:
            return bool(raw["device_on"])

        # 2) older versions might have 'on'
        if "on" in raw:
            return bool(raw["on"])

        # 3) fallback to relay_state
        system = raw.get("system", {})
        meta   = system.get("get_sysinfo", system)
        relay  = meta.get("relay_state")
        if relay is not None:
            return int(relay) == 1

        return False

    async def turn_on(self, name: str) -> bool:
        device = await self._connect(name)
        try:
            await device.turn_on()
            # 실제로 켜졌는지 재조회
            await device.update()
            state = self._parse_state(device.raw_state)
            logger.info(f"[Pyp100Service] '{name}' turn_on → {'on' if state else 'off'}")
            return state
        except Exception as e:
            logger.error(f"[Pyp100Service] turn_on '{name}' failed: {e}")
            return False
        finally:
            # 세션은 꼭 닫아 줍니다
            try:
                await device.session.close()
            except:
                pass

    async def turn_off(self, name: str) -> bool:
        device = await self._connect(name)
        try:
            await device.turn_off()
            await device.update()
            state = self._parse_state(device.raw_state)
            logger.info(f"[Pyp100Service] '{name}' turn_off → {'on' if state else 'off'}")
            return state
        except Exception as e:
            logger.error(f"[Pyp100Service] turn_off '{name}' failed: {e}")
            # 실패 시에도 raw_state 로 남아 있는 실제 상태를 리턴
            try:
                await device.update()
                return self._parse_state(device.raw_state)
            except:
                return True
        finally:
            try:
                await device.session.close()
            except:
                pass

    async def get_status(self, name: str) -> bool:
        device = await self._connect(name)
        try:
            raw = device.raw_state
            state = self._parse_state(raw)
            logger.info(f"[Pyp100Service] '{name}' status → {'on' if state else 'off'}")
            return state
        except Exception as e:
            logger.error(f"[Pyp100Service] get_status '{name}' failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Cannot get status for '{name}': {e}"
            )
        finally:
            try:
                await device.session.close()
            except:
                pass


# 싱글톤
pyp100_service = Pyp100Service()
