"""Универсальный оркестратор: парсит app_metadata.json и строит системный промт."""

import json
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT: Path = Path(__file__).resolve().parent

SYSTEM_ROLE: str = (
    "Ты — строгий DWH-архитектор уровня Senior. "
    "Твоя задача — преобразовать бизнес-вопрос пользователя на русском языке "
    "в чистый, исполняемый SQL-код для PostgreSQL 14+.\n\n"
    "ЖЁСТКИЕ ПРАВИЛА ФОРМАТА И СТИЛЯ:\n"
    "- Выводи СТРОГО чистый SQL-код без разметки markdown (БЕЗ ```sql и БЕЗ ```).\n"
    "- Никакого разговорного текста, пояснений, комментариев до или после кода.\n"
    "- Сразу первая строка должна быть валидным SQL-оператором (SELECT/WITH).\n"
    "- ВСЕ названия таблиц, колонок и ключевые слова SQL должны быть в ВЕРХНЕМ РЕГИСТРЕ (UPPERCASE).\n"
    "- ВСЕГДА принудительно оборачивай текстовые колонки в функцию UPPER() при сравнении в WHERE/JOIN.\n\n"
    "ПРИМЕР ПРАВИЛЬНОГО ФОРМАТА ОТВЕТА:\n"
    "SELECT T.ID FROM USERS T WHERE UPPER(T.STATUS) = 'ACTIVE' LIMIT 1"
)



def _render_schema(metadata: Dict[str, Any]) -> str:
    parts: list[str] = []
    parts.append("## АРХИТЕКТУРА ХРАНИЛИЩА ДАННЫХ (DWH)\n")
    parts.append(f"Домен: {metadata.get('domain_name', 'Unknown').upper()}\n")

    tables: Dict[str, Any] = metadata.get("tables", {})
    parts.append(f"Доступно таблиц: {len(tables)}\n")

    for table_name, table_meta in tables.items():
        # Принудительный верхний регистр для таблиц
        parts.append(f"\n### Таблица: {table_name.upper()}")
        parts.append(f"Описание: {table_meta.get('description', '').strip()}")
        parts.append("Колонки:")
        for col_name, col_desc in table_meta.get("columns", {}).items():
            # Принудительный верхний регистр для колонок
            parts.append(f"  - {col_name.upper()}: {col_desc}")

    return "\n".join(parts)



def _render_rules(metadata: Dict[str, Any]) -> str:
    rules: list[str] = metadata.get("strict_rules", [])
    if not rules:
        return ""
    parts: list[str] = ["\n## ЖЁСТКИЕ БИЗНЕС-ПРАВИЛА (ОБЯЗАТЕЛЬНЫ К ИСПОЛНЕНИЮ)"]
    for idx, rule in enumerate(rules, start=1):
        parts.append(f"{idx}. {rule}")
    return "\n".join(parts)


def build_universal_prompt(
    user_request: str, json_path: str = "app_metadata.json"
) -> str:
    """Собирает финальный промт для LLM из JSON-схемы + бизнес-запроса."""
    metadata_path: Path = PROJECT_ROOT / json_path
    with metadata_path.open("r", encoding="utf-8") as f:
        metadata: Dict[str, Any] = json.load(f)

    schema_block: str = _render_schema(metadata)
    rules_block: str = _render_rules(metadata)

    prompt: str = (
        f"{SYSTEM_ROLE}\n\n"
        f"{schema_block}\n"
        f"{rules_block}\n\n"
        f"## БИЗНЕС-ЗАПРОС ПОЛЬЗОВАТЕЛЯ\n{user_request.strip()}\n\n"
        f"## SQL-ОТВЕТ (ТОЛЬКО КОД, БЕЗ РАЗМЕТКИ):"
    )
    return prompt