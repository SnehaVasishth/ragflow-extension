import sys
from loguru import logger
from app.config.main import Config

VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

config = Config.get_environment()
if not config:
    raise ValueError("Configuration not found. Please check your environment settings.")

log_level = config["LOG_LEVEL"].upper()

if log_level not in VALID_LOG_LEVELS:
    log_level = "INFO"
    
logger.remove()

logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> - <level>{level: <8}</level> - {module} - <level>{message}</level>",
    level=log_level,
    enqueue=True
)
