import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    file = RotatingFileHandler(
        log_dir / "coffee-bot.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            console,
            file,
        ],
    )

    # Наш код логируем подробнее
    logging.getLogger("handlers").setLevel(logging.DEBUG)
    logging.getLogger("services").setLevel(logging.INFO)

    # Aiogram оставляем на INFO
    logging.getLogger("aiogram").setLevel(logging.INFO)