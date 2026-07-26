import logging
from config import LoggerSettings, settings


def prepare_logger(name: str, log_config: LoggerSettings):
    log = logging.getLogger(name)
    log.setLevel(level=log_config.level)

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt=log_config.LOG_DEFAULT_FORMAT,
            datefmt=log_config.datefmt,
        )
    )
    log.addHandler(handler)

    log.propagate = False # Не прокидывать сообщения по цепочке выше (в root логгер, который настраивается определением общим logging.basicConfig)

    return log


log = prepare_logger(__name__, settings.logger)


