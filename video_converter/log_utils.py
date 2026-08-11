import logging


def get_logger(logger_name: str) -> logging.Logger:
    """Return an idempotently configured package logger."""
    logger = logging.getLogger(f"video2text.{logger_name}")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    file_handler = logging.FileHandler("log.log", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
    )
    logger.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setFormatter(
        logging.Formatter("%(levelname)s %(message)s")
    )
    logger.addHandler(console)
    return logger
