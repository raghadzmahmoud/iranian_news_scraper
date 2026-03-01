"""
نظام التسجيل (Logging)
"""
import logging
from config.settings import LOG_LEVEL

# إعداد Logger
logger = logging.getLogger("iran_news_pipeline")
logger.setLevel(getattr(logging, LOG_LEVEL))

# Handler للـ Console
handler = logging.StreamHandler()
handler.setLevel(getattr(logging, LOG_LEVEL))

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)

logger.addHandler(handler)
