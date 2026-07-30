"""Безопасная инициализация переменных среды из .env файла."""

import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

PROJECT_ROOT: Path = Path(__file__).resolve().parent
ENV_PATH: Path = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_PATH)


def _require_env(var_name: str) -> str:
    import os

    value: Optional[str] = os.getenv(var_name)
    if value is None or not value.strip():
        sys.stderr.write(
            f"[CONFIG ERROR] Переменная окружения '{var_name}' не найдена или пуста.\n"
            f"Создайте файл {ENV_PATH} на основе .env.example и укажите значение.\n"
        )
        sys.exit(1)
    return value.strip()


OPENAI_API_KEY: str = _require_env("OPENAI_API_KEY")
OPENAI_MODEL: str = __import__("os").getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
OPENAI_BASE_URL: str = __import__("os").getenv(
    "OPENAI_BASE_URL", "https://api.openai.com/v1"
).strip()