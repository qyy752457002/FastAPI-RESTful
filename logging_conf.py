import logging

from logging.config import dictConfig

from config import DevConfig, config

def obfuscated(email: str, obfuscated_length: int):
    """Obfuscate email address for logging purposes."""
    # 获取email地址的前obfuscated_length个字符
    characters = email[:obfuscated_length]
    # 将email地址按照@符号分割成两部分
    first, last = email.split("@")
    # 返回前obfuscated_length个字符加上*号，再加上@符号，再加上后部分的email地址
    return characters + ("*" * (len(first) - obfuscated_length)) + "@" + last

class EmailObfuscationFilter(logging.Filter):
    def __init__(self, name: str = "", obfuscated_length: int = 2) -> None:
        # 初始化函数，设置name和obfuscated_length的默认值
        super().__init__(name)
        # 设置需要被混淆的email地址的长度
        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:
        # 如果record中包含email字段
        if "email" in record.__dict__:
            # 调用obfuscated函数，将email地址混淆
            record.email = obfuscated(record.email, self.obfuscated_length)
        # 返回True，表示该record需要被处理
        return True

# 定义日志处理器
handlers = ["default", "rotating_file"]
# 如果当前环境是生产环境，则添加logtail处理器
if config.ENV_STATE == "prod":
    handlers = ["default", "rotating_file", "logtail"]


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                    "default_value": "-",
                },
                "email_obfuscation": {
                    "()": EmailObfuscationFilter,
                    "obfuscated_length": 2 if isinstance(config, DevConfig) else 0,
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "(%(correlation_id)s) %(name)s:%(lineno)d - %(message)s",
                },
                "file": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    # For JsonFormatter, the format string just defines what keys are included in the log record
                    # It's a bit clunky, but it's the way to do it for now
                    "format": "%(asctime)s %(msecs)03d %(levelname)s %(correlation_id)s %(name)s %(lineno)d %(message)s", # noqa: E501
                },
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",  # could use logging.StreamHandler instead
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                "logtail": {
                    # https://betterstack.com/docs/logs/python/
                    "class": "logtail.LogtailHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id", "email_obfuscation"],
                    "source_token": config.LOGTAIL_API_KEY,  # gets passed to LogtailHandler constructor as kwargs
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filters": ["correlation_id", "email_obfuscation"],
                    "filename": "RESTful.log",
                    "maxBytes": 1024 * 1024,  # 1 MB
                    "backupCount": 2,
                    "encoding": "utf8",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default", "rotating_file"], "level": "INFO"},
                "RESTful": {
                    "handlers": handlers,
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                "databases": {"handlers": ["default"], "level": "WARNING"},
                "aiosqlite": {"handlers": ["default"], "level": "WARNING"},
            },
        }
    )
