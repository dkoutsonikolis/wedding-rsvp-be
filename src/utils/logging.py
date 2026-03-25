import logging
import sys


def setup_logging(debug: bool = False) -> None:
    """
    Configure logging for the application.

    This function sets up structured logging with:
    - Configurable log levels (DEBUG in development, INFO in production)
    - Consistent formatting with timestamps and logger names
    - Appropriate log levels for third-party libraries (uvicorn, SQLAlchemy)

    Why this approach:
    1. Centralized configuration - all logging setup in one place
    2. Environment-aware - different log levels for dev vs production
    3. Reduces noise - suppresses verbose logs from third-party libraries
    4. Structured format - easy to parse and search logs
    5. Standard output - works well with Docker and log aggregation tools

    Args:
        debug: If True, set log level to DEBUG. Otherwise, use INFO.
    """
    level = logging.DEBUG if debug else logging.INFO

    # Configure root logger with structured format
    # Format includes: timestamp, logger name, log level, and message
    # This makes it easy to identify where logs come from and when
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set specific loggers to appropriate levels to reduce noise:
    # - uvicorn: INFO (server logs, but not too verbose)
    # - uvicorn.access: WARNING (suppress HTTP access logs unless there's an issue)
    # - sqlalchemy.engine: WARNING in production, INFO in debug (SQL queries)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING if not debug else logging.INFO)


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get a logger instance for a module.

    Usage:
        logger = get_logger(__name__)
        logger.info("Something happened")
        logger.error("An error occurred", exc_info=True)

    Why use __name__:
    - Creates a logger hierarchy (e.g., "domains.users.service")
    - Makes it easy to identify where logs come from
    - Allows fine-grained control per module if needed

    Args:
        name: Logger name (usually __name__). If None, returns root logger.

    Returns:
        Logger instance
    """
    return logging.getLogger(name or __name__)
