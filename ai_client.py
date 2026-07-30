"""Изолированный сетевой клиент для работы с OpenAI-совместимым API."""

from typing import Optional

from openai import (
    APIConnectionError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

import config

_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
        )
    return _client


def get_sql_generation(prompt: str) -> str:
    """Отправляет промт в LLM и возвращает сгенерированный SQL."""
    try:
        client: OpenAI = _get_client()
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — генератор SQL. Отвечай только чистым SQL-кодом "
                        "без markdown-разметки и пояснений."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=1500,
        )
        return (response.choices[0].message.content or "").strip()

    except AuthenticationError:
        return (
            "-- ОШИБКА АВТОРИЗАЦИИ --\n"
            "API-ключ отклонён. Проверьте значение OPENAI_API_KEY в .env."
        )
    except APIConnectionError:
        return (
            "-- ОШИБКА СЕТЕВОГО ПОДКЛЮЧЕНИЯ --\n"
            "Не удалось связаться с API. Проверьте интернет и OPENAI_BASE_URL."
        )
    except RateLimitError:
        return (
            "-- ПРЕВЫШЕН ЛИМИТ ЗАПРОСОВ --\n"
            "Сервис временно ограничил число обращений. Повторите попытку позже."
        )
    except Exception as exc:
        return f"-- ВНУТРЕННЯЯ ОШИБКА LLM-КЛИЕНТА --\n{type(exc).__name__}: {exc}"