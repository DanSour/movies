import pandas as pd
import requests
import streamlit as st
from loguru import logger
from st_supabase_connection import SupabaseConnection, execute_query

logger.add(
    "logs/data_processing/debug.log",
    rotation="100 MB",
    compression="zip",
    level="DEBUG",
)


# Load the data from a SupabaseConnection. We're caching this so
# it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    """Загрузка данных

    Returns:
        pd.DataFrame: таблица фильмов из БД
    """
    st_supabase_client = st.connection(
        name="SupabaseConnection",
        type=SupabaseConnection,
        ttl=10,
    )
    request = execute_query(st_supabase_client.table("movies").select("*"), ttl=0)

    return pd.DataFrame(request.data)


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


def get_movie_type(movie_vars):
    """Определяет тип произведения (фильм, сериал, аниме и т.д.)
    на основе жанров и типа.

    Args:
        movie_vars (dict): Словарь с информацией о произведении (жанры, тип).

    Returns:
        _type_: Тип произведения как строка.
    """
    try:
        # Нормализация входных данных
        genres = set((movie_vars.get("genres", "") or "").lower().split(", "))
        movie_type = movie_vars.get("type", "")

        # Маппинг типов по умолчанию
        type_mapping = {
            "FILM": "Фильм", 
            "TV_SERIES": "Сериал", 
            "MINI_SERIES": "Сериал"
            }

        # Проверка специальных случаев
        if "аниме" in genres:
            return (
                "Аниме-сериал"
                if movie_type in ["TV_SERIES", "MINI_SERIES"]
                else "Мульт"
            )
        elif "мультфильм" in genres:
            return (
                "Мульт-сериал"
                if movie_type in ["TV_SERIES", "MINI_SERIES"]
                else "Мульт"
            )

        # Если специальные случаи не подходят, используем стандартный маппинг
        return type_mapping.get(movie_type, "Неизвестный тип")

    except AttributeError as e:
        # Логирование конкретной ошибки
        logger.error(f"Ошибка обработки данных в get_movie_type: {e}")
        return "Неизвестный тип"


def data_preparation(mov_vars):
    """Обрабатывает входящий файл и оставляет нужные данные

    Args:
        mov_vars (dict): словарь с большой информацией о произведении.

    Returns:
        dict: Нужная информация о произведении.
    """
    try:

        keys_to_keep = [
            "filmId",
            "nameRu",
            "posterUrl",
            "year",
            "genres",
            "rating",
            "filmLength",
            "type",
        ]
        mov_vars = {k: mov_vars.get(k, None) for k in keys_to_keep}

        mov_vars["name"] = mov_vars.pop("nameRu")

        mov_vars["genres"] = ", ".join([item["genre"] for item in mov_vars["genres"]])

        mov_vars["type"] = get_movie_type(mov_vars)
        mov_vars["url"] = f"https://www.kinopoisk.ru/film/{mov_vars.pop('filmId')}"

        return mov_vars

    except Exception as e:
        logger.error(f"Произошла ошибка data_preparation: {e}, mov_vars")
        return mov_vars


def film_dict(film_name) -> dict:
    """Ищет информацию о произведении по API кинопоиска

    Args:
        film_name (str): название произведения.

    Returns:
        dict: словарь с информацией о произведении.
    """
    url = "https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword"
    # Заголовки запроса
    headers = {
        "X-API-KEY": st.secrets["API_KEY"],
        "Content-Type": "application/json",
    }
    # Параметры запроса
    params = {"keyword": film_name}  # Ключевое слово для поиска

    try:
        response = requests.get(url, headers=headers, params=params, timeout=100)

        # Проверяем, успешен ли запрос
        if response.status_code == 200:
            film_data = response.json()  # Преобразуем ответ в JSON
            return film_data["films"][0] if film_data["films"] else None
        else:
            logger.error(f"Ошибка film_dict: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        # print(f'Произошла ошибка: {e}')
        st.error("Film_dict error", icon="🚨")
        logger.error(f"Ошибка film_dict: {e}")


# Сохранение данных обратно в CSV файл
def add_film(new_mov):
    """Ищет информацию о произведении и добавляет в бд

    Args:
        new_mov (str): название произведения.
    """
    try:
        st_supabase_client = st.connection(
            name="SupabaseConnection",
            type=SupabaseConnection,
            ttl=10,
        )

        mov_vars = film_dict(new_mov.lower())

        if mov_vars is None:
            execute_query(
                st_supabase_client.table("offered_movies").insert(
                    # {"name": new_mov.lower(), "img": None, "year": None}
                    {"name": new_mov.lower(), "posterUrl": "-"}
                ),
                ttl=0,
            )
            logger.warning(f"mov_vars is None, add_film: {new_mov}")
            return

        mov_data = data_preparation(mov_vars)
        # logger.debug(mov_data)
        if mov_data is None:
            execute_query(
                st_supabase_client.table("offered_movies").insert(
                    {
                        "name": new_mov.lower(),
                        "img": "img",
                    }
                ),
            )
            logger.error(f"Ошибка при обработке данных: {new_mov}")
        else:
            execute_query(
                st_supabase_client.table("offered_movies").insert(mov_data),
                # ttl=1
            )

    except Exception as e:
        error_msg = str(
            e
        ).lower()  # Приводим сообщение к нижнему регистру для универсальности

        # Проверяем наличие кода ошибки 23505 или ключевых слов
        if "23505" in error_msg or "duplicate key" in error_msg:
            logger.warning(f"Попытка добавить дубликат: {e} {new_mov}")
        else:
            st.error(f"This is an error: {e}", icon="🚨")
            logger.error(f"Ошибка add_film: {e}")
