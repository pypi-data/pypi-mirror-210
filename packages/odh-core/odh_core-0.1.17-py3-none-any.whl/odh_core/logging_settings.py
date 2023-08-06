__doc__ = """

https://docs.djangoproject.com/en/4.0/topics/logging/
"""
import os


LOGGING_DEV = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "utc_color": {
            # NOTE: you need to include the pythonfile in the classname
            # format is set dynamically in the formatter class to include color
            "()": "odh_core.logger.UTCColorFormatter",
            # uvicorn uses need to have datefmt explicitly set
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "utc": {
            "()": "odh_core.logger.UTCFormatter",
            "format": "[%(asctime)s.%(msecs)03dZ] %(levelname)s : %(name)s : %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "utc_color"},
        "file": {
            # no color in log file
            "formatter": "utc",
            "filename": "odh.log",
            "class": "logging.FileHandler",
            # only log WARNING and above to file
            "level": "WARNING",
        },
    },
    "filters": {
        "hide_gql_schema": {
            "()": "odh_core.logger.HideMessageStartswith",
            "text": '<<< {"data":{"__schema":',
        },
        "hide_gql_IntrospectionQuery": {
            "()": "odh_core.logger.HideMessageStartswith",
            "text": '>>> {"query": "query IntrospectionQuery',
        },
    },
    # root sets default values and subsequent loggers can override the values
    # "root": {"handlers": ["console"], "level": "DEBUG"},
    "root": {"handlers": ["console", "file"], "level": "DEBUG"},
    "loggers": {
        "gql.transport.aiohttp": {
            "level": "DEBUG",
            "filters": ["hide_gql_schema", "hide_gql_IntrospectionQuery"],
            # "handlers": ["file"],
        },
        "odh": {
            "level": "DEBUG",
            # "handlers": ["console"],
        },
        # hide filewatcher debug messages
        "watchfiles.main": {
            "level": "WARNING",
        },
    },
}

LOGGING_PROD = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "utc_color": {
            # NOTE: you need to include the pythonfile in the classname
            # format is set dynamically in the formatter class to include color
            "()": "odh_core.logger.UTCColorFormatter",
            # uvicorn uses need to have datefmt explicitly set
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "utc": {
            "()": "odh_core.logger.UTCFormatter",
            "format": "[%(asctime)s.%(msecs)03dZ] %(levelname)s : %(name)s : %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "utc_color"},
        "file": {
            # no color in log file
            "formatter": "utc",
            "filename": "odh.log",
            "class": "logging.FileHandler",
            # only log WARNING and above to file
            "level": "WARNING",
        },
    },
    "filters": {
        "hide_gql_schema": {
            "()": "odh_core.logger.HideMessageStartswith",
            "text": '<<< {"data":{"__schema":',
        },
        "hide_gql_IntrospectionQuery": {
            "()": "odh_core.logger.HideMessageStartswith",
            "text": '>>> {"query": "query IntrospectionQuery',
        },
    },
    # root sets default values and subsequent loggers can override the values
    # "root": {"handlers": ["console"], "level": "DEBUG"},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "gql.transport.aiohttp": {
            "level": "DEBUG",
            "filters": ["hide_gql_schema", "hide_gql_IntrospectionQuery"],
            # "handlers": ["file"],
        },
        "odh": {
            "level": "INFO",
            # "handlers": ["console"],
        },
        # hide filewatcher debug messages
        "watchfiles.main": {
            "level": "WARNING",
        },
    },
}

# auto set logging settings based on REMOTE_CONTAINERS env var
LOGGING_AUTO = LOGGING_PROD
if os.getenv("REMOTE_CONTAINERS", default="False").lower() in ("true", "1", "t"):
    # since vscode 1.50 remote containers will automatically
    # set env to REMOTE_CONTAINERS=true
    # see: https://github.com/microsoft/vscode-remote-release/issues/3517
    LOGGING_AUTO = LOGGING_DEV
    print("REMOTE_CONTAINERS=True, setting logging to LOGGING_DEV")

if os.getenv("LOGG_SETTING") == "PROD":
    LOGGING_AUTO = LOGGING_PROD
    print("LOGG_SETTING=PROD, setting logging to LOGGING_PROD")
elif os.getenv("LOGG_SETTING") == "DEV":
    LOGGING_AUTO = LOGGING_DEV
    print("LOGG_SETTING=DEV, setting logging to LOGGING_DEV")
