from logging.config import dictConfig
import logging

from pydantic import BaseModel
from uvicorn.config import LOGGING_CONFIG

from constants import LOG_FORMAT


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = 'api'
    LOG_FORMAT: str = LOG_FORMAT
    LOG_LEVEL: str = 'DEBUG'

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': LOG_FORMAT,
        },
    }
    handlers = {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
    }
    loggers = {
        'api': {'handlers': ['default'], 'level': LOG_LEVEL},
    }


dictConfig(LogConfig().dict())
logger = logging.getLogger('api')
LOGGING_CONFIG['formatters']['default']['fmt'] = LOG_FORMAT
LOGGING_CONFIG['formatters']['access']['fmt'] = LOG_FORMAT
