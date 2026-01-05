import pandas as pd
import requests
import streamlit as st
from loguru import logger
from st_supabase_connection import execute_query

from scripts.data_processing import init_supabase_client


# Load the data from a SupabaseConnection. We're caching this so
# it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_movies():
    """Загрузка данных

    Returns:
        pd.DataFrame: таблица фильмов из БД
    """
    st_supabase_client = init_supabase_client()
    request = execute_query(
        st_supabase_client.table("movies").select("*").order("year"), ttl=0
    )

    return pd.DataFrame(request.data)


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
    film_name = film_name.lower()
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


def data_preparation(raw_data) -> dict:
    """Processes the input data and extracts the required information.

    Args:
        raw_data (dict): Dictionary containing extensive information about the movie.

    Returns:
        dict: Extracted information about the movie.
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
        mov_vars = {k: raw_data.get(k, None) for k in keys_to_keep}

        mov_vars["name"] = mov_vars.pop("nameRu")
        if mov_vars["name"] is None:
            mov_vars["name"] = raw_data.get('nameEn')
        mov_vars["url"] = f"https://www.kinopoisk.ru/film/{mov_vars.pop('filmId')}"

        mov_vars["genres"] = ", ".join([item["genre"] for item in mov_vars["genres"]])

        mov_vars["rating"] = (
            0.0 if mov_vars["rating"] == "null" else float(mov_vars["rating"])
        )
        mov_vars["type"] = get_movie_type(mov_vars)

        return mov_vars

    except Exception as e:
        logger.error(f"data_preparation error: {e}, mov_vars")
        return None


# Сохранение данных в БД рекомендаций
def offer_film(new_mov):
    """Ищет информацию о произведении и добавляет в БД "Рекомендованные фильмы"

    Args:
        new_mov (str): название произведения
    """
    try:
        st_supabase_client = init_supabase_client()
        db_table = "offered_movies"

        raw_data = search_film(new_mov)

        if raw_data is not None:
            mov_data = data_preparation(raw_data)
            logger.success(f"Данные преобразованы: {new_mov} -> {mov_data['name']}")

            if mov_data is not None:
                execute_query(
                    st_supabase_client.table(f"{db_table}").insert(mov_data), ttl=0
                )
                logger.success(f"Успешно добавлен: {mov_data['name']}")
                return

        execute_query(
            st_supabase_client.table(f"{db_table}").insert(
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
            logger.error(f"offer_film error: {e}")


# Флаг: была ли отправлена форма
def movie_form():
    submitted = st.session_state.get("submitted", False)

    # Если не отправлена форма, то создаем форму
    if not submitted:
        with st.form("add_movie_form"):
            # Ввод фильма
            mov = st.text_input(
                "Название фильма",
                label_visibility="collapsed",
                placeholder="Предложить фильм...",
                key="new_mov",
            )
            send = st.form_submit_button(
                ":film_projector: Предложить",
                use_container_width=True,
                type="secondary",
            )
            # .strip() возвращает слово без пробелов в начале и конце
            if send and mov.lower().strip():
                # state того что отправили
                st.session_state["submitted"] = True
                if mov.lower() in ["хуй", "пенис", "пизда"]:
                    st.session_state["bad_word"] = mov
                else:
                    offer_film(mov)
                st.rerun()
    else:
        bad_word = st.session_state.get("bad_word")
        if bad_word:
            st.error(
                f"Себе {bad_word} порекомендуй, клоун 👊😡",
                icon="🤡",
            )
            return
        else:
            st.success("Спасибо за предложение!!", icon="✅")
        if st.button("Предложить еще"):
            for key in ("submitted", "bad_word", "new_mov"):
                st.session_state.pop(key, None)
                st.rerun()


def process_movie(movie_name: str):
    """
    Полная обработка фильма: поиск + подготовка

    Args:
        name: Название фильма

    Returns:
        Готовые данные для БД или None
    """
    # from scripts.scripts_movies import data_preparation, search_film

    raw_data = search_film(movie_name)

    if raw_data is not None:
        mov_data = data_preparation(raw_data)

        if mov_data is not None:
            del mov_data["url"]  # Убираем колонку url

        return mov_data
    return None
