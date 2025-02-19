import pandas as pd
import requests
import streamlit as st
from loguru import logger
from st_supabase_connection import SupabaseConnection, execute_query


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
        ttl=20,
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
        type_mapping = {"FILM": "Фильм", "TV_SERIES": "Сериал", "MINI_SERIES": "Сериал"}

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
        return None


def search_film(film_name) -> dict:
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
        response = requests.get(url, headers=headers, params=params, timeout=4)

        # Проверяем, успешен ли запрос
        if response.status_code == 200:
            film_data = response.json()  # Преобразуем ответ в JSON
            films = film_data.get("films", [])
            return films[0] if films else None
        else:
            logger.error(f"response err: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        # print(f'Произошла ошибка: {e}')
        st.error("search_film error", icon="🚨")
        logger.error(f"Ошибка search_film: {e}")


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
        new_mov = new_mov.lower()
        mov_vars = search_film(new_mov)

        if mov_vars is not None:
            mov_data = data_preparation(mov_vars)
            logger.success(
                f"Данные преобразованы: {new_mov} -> {mov_data['name']}"
            )

            if mov_data is not None:
                execute_query(
                    st_supabase_client.table("offered_movies").insert(mov_data),
                    ttl=0
                )
                logger.success(f"Успешно добавлен: {mov_data['name']}")

                return

        execute_query(
            st_supabase_client.table("offered_movies").insert(
                {"name": new_mov, "posterUrl": "-"}
            ),
            ttl=0,
        )
        logger.success(f"Добавлено только название {new_mov}")

    except Exception as e:
        # Приводим сообщение к нижнему регистру для универсальности
        error_msg = str(e).lower()

        # Проверяем наличие кода ошибки 23505 или ключевых слов
        if "23505" in error_msg or "duplicate key" in error_msg:
            logger.warning(f"Попытка добавить дубликат: {new_mov}")
        else:
            st.error(f"This is an error: {e}", icon="🚨")
            logger.error(f"Ошибка add_film: {e}")
