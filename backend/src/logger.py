import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path


class JsonFormatter(logging.Formatter):
    def format(self, record):
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[1]:
            entry["traceback"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)


def setup_logger(name="rdo_automator", log_path=None, level=None):
    if level is None:
        level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)

    if log_path is None:
        log_path = Path(os.environ.get("LOG_PATH", "/tmp/rdo_automator.log"))

    log_path.parent.mkdir(parents=True, exist_ok=True)

    use_json = os.environ.get("LOG_FORMAT", "").lower() == "json"
    formatter = (
        JsonFormatter()
        if use_json
        else logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(str(log_path), encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    return logger


logger = setup_logger()
