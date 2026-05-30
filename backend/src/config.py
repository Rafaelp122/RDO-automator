import os
from dataclasses import dataclass, field


def _load_dotenv():
    # Carrega variáveis do arquivo .env no diretório atual se ele existir
    try:
        # Busca o .env no diretório de execução ou no diretório pai/raiz do backend
        dotenv_path = ".env"
        if not os.path.exists(dotenv_path) and os.path.exists("../.env"):
            dotenv_path = "../.env"
            
        with open(dotenv_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                # Remove aspas se houver
                val = val.strip().strip("'\"")
                os.environ.setdefault(key.strip(), val)
    except Exception:
        pass


# Carrega as variáveis do arquivo .env antes de iniciar as configurações
_load_dotenv()


def _parse_allowed_origins(raw: str) -> list[str]:
    return [o.strip() for o in raw.split(",") if o.strip()]


@dataclass
class Settings:
    allowed_origins: list[str] = field(
        default_factory=lambda: _parse_allowed_origins(
            os.environ.get(
                "ALLOWED_ORIGINS",
                "http://localhost:3000,http://localhost:5173,https://rdo.vercel.app",
            )
        )
    )

    max_upload_mb: int = int(os.environ.get("MAX_UPLOAD_MB", "32"))

    api_key: str = os.environ.get("API_KEY", "")

    log_level: str = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_format: str = os.environ.get("LOG_FORMAT", "")
    log_path: str = os.environ.get("LOG_PATH", "/tmp/rdo_automator.log")

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


settings = Settings()
