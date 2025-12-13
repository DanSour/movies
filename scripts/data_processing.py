import pandas as pd
import streamlit as st
from loguru import logger
from st_supabase_connection import SupabaseConnection, execute_query


def init_supabase_client():
    if "st_supabase_client" not in st.session_state:
        try:
            st.session_state.st_supabase_client = st.connection(
                name="SupabaseConnection",
                type=SupabaseConnection,
                ttl=20,
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            st.error(f"This is an error: {e}", icon="🚨")
    return st.session_state.st_supabase_client


def authenticate(username: str, password: str) -> dict:
    """Аутентификация пользователя

    Args:
        username (str): Почта которая зарегистрирована для изменения бд
        password (str): Зарегистрированный пароль

    Returns:
        dict: Словарь с данными об успешном подключении и клиентом supabase_client
    """
    client = init_supabase_client()
    response = client.auth.sign_in_with_password(
        {"email": username, "password": password}
    )
    return {"response": bool(response), "client": client}


def filter_dataframe(df, selected_types, years):
    """Фильтрует DataFrame по выбранным типам контента и диапазону лет.

    Args:
        df (pd.DataFrame): Исходный DataFrame.
        selected_types (list): Список выбранных типов контента.
        years (tuple): Диапазон лет (min_year, max_year).

    Returns:
        pd.DataFrame: Отфильтрованный DataFrame.
    """
    try:
        year_filter = df["year"].between(years[0], years[1])
        if selected_types:
            type_filter = df["type"].isin(selected_types)
            return df[year_filter & type_filter]
        else:
            return df[year_filter]
    except KeyError:
        st.error("Колонка 'type' или 'year' не найдена в DataFrame.")
        return pd.DataFrame()


def db_editing(type, function, name, st_supabase_client):
    from scripts.scripts_movies import data_preparation, search_film

    """Ищет информацию о произведении и добавляет в бд

    Args:
        new_mov (str): название произведения.
    """
    tables = {
        "🎬 Movie": "movies",
        "🎮 Game": "games"
    }

    actions = {
        "➕ Insert": "insert",
        "🗑️ Delete": "delete"
    }

    db_table = tables[type]  # "movies"
    action = actions[function]
# Надо добавить логику 
# если фильм - отдаем в функицю в которую передаем название, экшен и дб
# если игра - отдаем в другую функцию обработки и считывания, но
# действия (add/delete) отдельная функция
    try:
        if db_table == "movies":
            new_mov = name.lower()
            mov_vars = search_film(new_mov)

            if mov_vars is not None:
                mov_data = data_preparation(mov_vars)

                if mov_data is not None:
                    del mov_data["url"]  # Убираем колонку url

                    # Выполняем операцию в зависимости от ключевого слова
                    if action == "insert":
                        execute_query(
                            st_supabase_client.table(f"{db_table}").insert(mov_data), ttl=0
                        )
                    elif action == "delete":
                        # for success message
                        action = "delet"
                        execute_query(
                            st_supabase_client.table(f"{db_table}")
                            .delete()
                            .eq("name", mov_data["name"]),
                            ttl=0,
                        )
                    else:
                        raise ValueError(f"Неподдерживаемая операция: {action}")

                    logger.success(f"Successfully {action}ed: {mov_data['name']}")
                    st.success(f"Successfully {action}ed: {mov_data['name']}")
                    return

        logger.info("Фильм не найден")
        st.info("Фильм не найден")

    except Exception as e:
        # Приводим сообщение к нижнему регистру для универсальности
        error_msg = str(e).lower()

        # Проверяем наличие кода ошибки 23505 или ключевых слов
        if "23505" in error_msg or "duplicate key" in error_msg:
            logger.warning(f"Попытка добавить дубликат: {new_mov}")
            st.warning("Дубликат")
        else:
            st.error(f"This is an error: {e}", icon="🚨")
            logger.error(f"Ошибка: {e}")
