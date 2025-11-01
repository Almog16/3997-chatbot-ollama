import logging
import logging.config
import sys
from logging import LogRecord

LOGGER = logging.getLogger()


class PrettyPrintFormatter(logging.Formatter):
    """Formatter for making logs look nice in local development."""

    def format(self: "PrettyPrintFormatter", record: LogRecord) -> str:
        log_entry = f"{record.levelname}: [{record.name}] {record.getMessage()}"
        if record.exc_info:
            log_entry += f"\nException: {self.formatException(record.exc_info)}"
        return log_entry


def initialize_logger() -> None:
    # Disable all other loggers in imported modules
    logging.config.dictConfig({"version": 1, "disable_existing_loggers": True})
    _set_root_logger()


def _set_root_logger() -> None:
    logger = logging.getLogger()
    logger.handlers.clear()
    formatter = PrettyPrintFormatter()
    logger.setLevel(logging.DEBUG)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
