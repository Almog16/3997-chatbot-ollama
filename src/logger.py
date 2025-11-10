import logging
import logging.config
import sys
from logging import LogRecord

LOGGER = logging.getLogger()


class PrettyPrintFormatter(logging.Formatter):
    """A custom log formatter for enhancing readability during local development.

    This formatter presents log messages in a clean, easy-to-read format,
    making it simpler to debug the application. It includes the log level,
    the logger's name, and the message itself. If an exception is present,
    it will be formatted and appended to the log entry.
    """

    def format(self: "PrettyPrintFormatter", record: LogRecord) -> str:
        """Formats a log record into a human-readable string.

        Args:
        ----
            record: The `LogRecord` to be formatted.

        Returns:
        -------
            A string representing the formatted log entry.

        """
        log_entry = f"{record.levelname}: [{record.name}] {record.getMessage()}"
        if record.exc_info:
            log_entry += f"\nException: {self.formatException(record.exc_info)}"
        return log_entry


def initialize_logger() -> None:
    """Sets up the root logger for the application.

    This function configures the application's logging system by first
    disabling all existing loggers from imported modules. This ensures that
    only the application's own logs are displayed. It then calls
    `_set_root_logger` to configure the root logger with the custom
    `PrettyPrintFormatter`.
    """
    # Disable all other loggers in imported modules
    logging.config.dictConfig({"version": 1, "disable_existing_loggers": True})
    _set_root_logger()


def _set_root_logger() -> None:
    """Configures the root logger with a custom formatter and stream handler.

    This internal function clears any existing handlers on the root logger,
    sets the logging level to DEBUG, and adds a new handler that streams logs
    to standard output using the `PrettyPrintFormatter`.
    """
    logger = logging.getLogger()
    logger.handlers.clear()
    formatter = PrettyPrintFormatter()
    logger.setLevel(logging.DEBUG)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
