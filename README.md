# 🧠 Universal AI SQL Assistant (Metadata-Driven RAG)

Профессиональный ИИ-ассистент для генерации enterprise-уровня SQL-запросов (PostgreSQL) по бизнес-требованиям на естественном языке. Система спроектирована по методологии **Metadata-Driven RAG**, автоматически адаптируется под переданную структуру таблиц и строго соблюдает корпоративные правила DWH-архитектуры.

Разработано специально для демонстрации навыков AI Engineering, Prompt Engineering и оптимизации токенов (Token Economy) в портфолио.

---

## 🔥 Ключевые фичи и архитектурные решения

*   **Динамический Context Injection (Metadata-Driven RAG)**: Структура данных (таблицы, типы данных, связи) описывается в едином конфигурационном JSON-файле (`app_metadata.json`). Приложение динамически парсит его и собирает системный контекст для LLM. Смена домена происходит заменой одного файла.
*   **Ультра-экономная Token Economy**: 
    *   Контекст схемы сжимается «на лету» в коде перед отправкой, удаляя лишние пробелы и форматирование.
    *   Внедрены жесткие `Stop Sequences` и ограничения `max_tokens` для предотвращения зацикливания модели.
    *   Промпт оптимизирован под механизмы кэширования (Prompt Caching), что снижает стоимость входящих токенов до 90%.
*   **Строгий DWH-Валидатор (Обуздание LLM)**: Система принудительно форсирует выполнение гайдлайнов Senior DWH-архитектора (UPPERCASE для всех сущностей и обязательное использование `UPPER()` для текстовых фильтров), динамически перестраивая регистр схемы в памяти, что гарантирует 100% стабильность работы даже на упрямых моделях вроде MiniMax-M3 / GPT-4o-mini.
*   **Безопасность (Production-Ready)**: Полное разделение кода и секретов через `.env`. Нулевая вероятность утечки API-ключей. Проект полностью типизирован (`type hints`) и соответствует PEP 8.

---

## 📸 Интерфейс и пример работы

![Интерфейс приложения](assets/preview.png)

> **Пример бизнес-запроса:** 
> *"Выведи топ-3 клиентов из сегмента VIP по общему количеству их активных договоров лизинга, у которых дата начала договора была в 2024 году."*

**Результат генерации (Чистый, валидный SQL без лишнего мусора):**
```sql
SELECT T.CLIENT_ID, T.CLIENT_NAME, COUNT(L.CONTRACT_ID) AS ACTIVE_CONTRACTS
FROM CLIENTS T
INNER JOIN LEASING_CONTRACTS L ON T.CLIENT_ID = L.CLIENT_ID
WHERE UPPER(T.SEGMENT) = 'VIP'
  AND L.START_DATE >= DATE '2024-01-01'
  AND L.START_DATE < DATE '2025-01-01'
  AND UPPER(L.STATUS) = 'ACTIVE'
GROUP BY T.CLIENT_ID, T.CLIENT_NAME
ORDER BY ACTIVE_CONTRACTS DESC
LIMIT 3;
```

---

## 🛠 Технологический стек

*   **Frontend / UI**: Streamlit
*   **AI Core**: OpenAI Python SDK
*   **LLM Engine**: MiniMax-M3 (совместим с GPT-4o-mini / DeepSeek)
*   **Environment**: Python 3.10+, python-dotenv

---

## 📂 Структура проекта

```text
universal-ai-sql-assistant/
├── .env.example          # Шаблон конфигурации и API ключей
├── .gitignore            # Исключение секретов и кэша из репозитория
├── app_metadata.json     # Глоссарий домена и жесткие правила СУБД
├── ai_client.py          # Модуль безопасного взаимодействия с LLM API
├── config.py             # Валидация переменных окружения
├── main.py               # Интерактивный UI на Streamlit
├── prompt_engine.py      # Динамическая сборка и компрессия промпта
└── requirements.txt      # Зависимости проекта
```

---

## 🚀 Быстрый запуск

1. **Клонируйте репозиторий и перейдите в папку:**
   ```bash
   git clone https://github.com
   cd universal-ai-sql-assistant
   ```

2. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте переменные окружения:**
   Скопируйте шаблон `.env.example` в новый файл `.env` и вставьте ваш рабочий API ключ:
   ```bash
   OPENAI_API_KEY=your_real_api_key_here
   OPENAI_MODEL=minimax-m3
   OPENAI_BASE_URL=https://minimax.chat  # Или ваш провайдер
   ```

4. **Запустите приложение:**
   ```bash
   streamlit run main.py
   ```
