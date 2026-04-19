import logging
from pathlib import Path
from datetime import datetime


def setup_logger(name: str, log_dir: Path = None) -> logging.Logger:

    if log_dir is None:
        log_dir = Path.home() / ".diplom_simulator" / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Файл лога
    log_file = log_dir / f"{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Консоль (только важное)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Формат
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger