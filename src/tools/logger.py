from src.tools.singleton import Singleton
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

class Logger(metaclass=Singleton):
    def __init__(self, name: str = "app_logger", log_dir: str = "logs", level: str = "DEBUG"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.DEBUG))
        self.logger.propagate = False

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_filename = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Rotating File Handler (5MB max, 3 backups)
        file_handler = RotatingFileHandler(log_filename, maxBytes=5*1024*1024, backupCount=3)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def get_logger(self):
        return self.logger
