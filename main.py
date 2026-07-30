"""Точка входа Streamlit-приложения Universal AI SQL Assistant."""

import json
from pathlib import Path

import streamlit as st

import ai_client
import prompt_engine

PROJECT_ROOT: Path = Path(__file__).resolve().parent
METADATA_PATH: Path = PROJECT_ROOT / "app_metadata.json"


@st.cache_data
def load_metadata(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def render_sidebar(metadata: dict) -> None:
    with st.sidebar:
        st.title("🧠 Universal AI SQL Assistant")
        st.caption("Metadata-Driven RAG для DWH")
        st.markdown("---")
        st.subheader("📚 Подключённый домен")
        st.info(metadata.get("domain_name", "—"))

        with st.expander("🗂️ Структура репозитория таблиц"):
            tables = metadata.get("tables", {})
            for table_name, table_meta in tables.items():
                st.markdown(f"**{table_name}**")
                st.caption(table_meta.get("description", ""))
                cols = table_meta.get("columns", {})
                for col_name, col_desc in cols.items():
                    st.markdown(f"- `{col_name}` — {col_desc}")
                st.markdown("")

        st.markdown("---")
        st.caption("v1.0 · PostgreSQL · OpenAI-compatible API")


def main() -> None:
    st.set_page_config(
        page_title="Universal AI SQL Assistant",
        page_icon="🧠",
        layout="wide",
    )

    try:
        metadata: dict = load_metadata(METADATA_PATH)
    except FileNotFoundError:
        st.error(f"Не найден файл метаданных: {METADATA_PATH}")
        st.stop()
    except json.JSONDecodeError as exc:
        st.error(f"Ошибка разбора app_metadata.json: {exc}")
        st.stop()

    render_sidebar(metadata)

    st.title("🧠 Генератор SQL по бизнес-запросу")
    st.write(
        "Опишите задачу на русском языке. Сервис использует схему DWH из "
        "`app_metadata.json` и сгенерирует валидный PostgreSQL-запрос."
    )

    user_request: str = st.text_area(
        label="Бизнес-запрос",
        placeholder=(
            "Например: Покажи топ-5 клиентов сегмента VIP по сумме активных "
            "договоров лизинга на текущую дату."
        ),
        height=160,
    )

    generate_clicked: bool = st.button(
        "⚡ Сгенерировать SQL", type="primary", use_container_width=True
    )

    if generate_clicked:
        if not user_request.strip():
            st.warning("Введите текст запроса перед генерацией.")
            return

        with st.spinner("🧠 DWH-архитектор формирует SQL..."):
            try:
                prompt: str = prompt_engine.build_universal_prompt(
                    user_request=user_request,
                    json_path="app_metadata.json",
                )
                generated_sql: str = ai_client.get_sql_generation(prompt)
            except Exception as exc:
                st.error(f"Сбой при генерации: {type(exc).__name__}: {exc}")
                return

        is_error: bool = generated_sql.startswith("--")
        if is_error:
            st.error(generated_sql)
        else:
            st.success("✅ SQL успешно сгенерирован")
            st.code(generated_sql, language="sql")


if __name__ == "__main__":
    main()