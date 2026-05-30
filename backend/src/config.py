import os
from dataclasses import dataclass, field


def _parse_allowed_origins(raw: str) -> list[str]:
    return [o.strip() for o in raw.split(",") if o.strip()]


@dataclass
class Settings:
    allowed_origins: list[str] = field(default_factory=lambda: _parse_allowed_origins(
        os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,https://rdo.vercel.app")
    ))

    max_upload_mb: int = int(os.environ.get("MAX_UPLOAD_MB", "50"))

    log_level: str = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_format: str = os.environ.get("LOG_FORMAT", "")
    log_path: str = os.environ.get("LOG_PATH", "/tmp/rdo_automator.log")

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


settings = Settings()
