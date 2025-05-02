from app.config import settings
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print(f"PLUGS_RAW: {settings.PLUGS_RAW!r}")
print(f"PLUGS: {list(settings.PLUGS)}") 