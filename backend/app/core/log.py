import logging.config
import typing

from . import conf


def setup_default_logging(level: typing.Optional[str] = None):
    """Set up basic configuration with default formatter."""

    if level is None:
        level = conf.log.level

    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': conf.log.internal.format,
            },
            'uvicorn_access': {
                '()': 'uvicorn.logging.AccessFormatter',
                'fmt': '[%(process)s] [%(levelname)s] [%(name)s] %(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
            },
        },
        'handlers': {
            'default': {'formatter': 'default', 'class': 'logging.StreamHandler'},
            'uvicorn_access': {
                'formatter': 'uvicorn_access',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': level.upper(),
                'propagate': True,
            },
            'uvicorn.access': {
                'handlers': ['uvicorn_access'],
                'level': level.upper(),
                'propagate': False,
            },
        },
    }

    logging.config.dictConfig(config)

    return config
