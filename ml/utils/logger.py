import logging
import sys
import datetime
from pathlib import Path
from typing import Any, Optional
from ml.configs import LOGS_DIR

class EnterpriseLogger:
    """
    Structured production logger with console and file rotation support.
    Designed for MLOps tracking and audit trails.
    """
    def __init__(self, name: str = "MLOps-Engine"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            # Console Handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
            
            # File Handler
            log_file = LOGS_DIR / f"mlops_execution_{datetime.date.today().strftime('%Y_%m_%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def info(self, message: str, **kwargs):
        msg = f"{message} | {kwargs}" if kwargs else message
        self.logger.info(msg)

    def warning(self, message: str, **kwargs):
        msg = f"{message} | {kwargs}" if kwargs else message
        self.logger.warning(msg)

    def error(self, message: str, exc_info: Optional[Exception] = None, **kwargs):
        msg = f"{message} | {kwargs}" if kwargs else message
        self.logger.error(msg, exc_info=exc_info)

    def debug(self, message: str, **kwargs):
        msg = f"{message} | {kwargs}" if kwargs else message
        self.logger.debug(msg)

# Global singleton logger
logger = EnterpriseLogger("Amazon-AI-MLOps")
