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
    """Data uploading

    Returns:
        pd.DataFrame: movies table from DB
    """
    st_supabase_client = init_supabase_client()
    request = execute_query(
        st_supabase_client.table("movies").select("*").order("year"), ttl=0
    )

    return pd.DataFrame(request.data)


def get_movie_type(movie_vars):
    """Determines the type of a movie based on its genres and type.

    Args:
        movie_vars (dict): Dictionary with information about the movie (genres, type).

    Returns:
        _type_: The type of the movie as a string.
    """
    try:
        # Extract genres and type from the movie_vars dictionary
        genres = set((movie_vars.get("genres", "") or "").lower().split(", "))
        movie_type = movie_vars.get("type", "")

        # Define a mapping for standard movie types
        type_mapping = {"FILM": "Фильм", "TV_SERIES": "Сериал", "MINI_SERIES": "Сериал"}

        # Check for special cases based on genres
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

        # Return the mapped type or a default value if not found
        return type_mapping.get(movie_type, "Неизвестный")

    except AttributeError as e:
        # Handle cases where movie_vars is not a dictionary or has unexpected structure
        logger.error(f"get_movie_type error: {e}")
        return "Неизвестный тип"


def search_by_id(film_name) -> dict:
    """Searches for information about a film using its ID with the Kinopoisk API.

    Args:
        film_name (str): The ID of the film to search for.

    Returns:
        dict: Dictionary with information about the film.
    """
    url = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{film_name}"

    # Headers for the API request
    headers = {
        "X-API-KEY": st.secrets["API_KEY"],
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=4)

        # Check if the response is successful
        if response.status_code == 200:

            film_data = response.json()  # Parse the JSON response

            if film_data["filmLength"] is not None:
                film_length = int(film_data["filmLength"])
                film_data["filmLength"] = f"{film_length // 60:02d}:{film_length % 60:02d}"

            return film_data
        else:
            logger.error(f"search_by_id response error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error("Kinopoisk id search issue", icon="🚨")
        logger.error(f"search_by_id error: {e}")


def search_film(film_name) -> dict:
    """Searches for information about a film using the Kinopoisk API.

    Args:
        film_name (str): The name of the film to search for.

    Returns:
        dict: Dictionary with information about the film.
    """
    if (film_name.isdigit()):
        film_data = search_by_id(film_name)
        return film_data

    url = "https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword"

    # Headers for the API request
    headers = {
        "X-API-KEY": st.secrets["API_KEY"],
        "Content-Type": "application/json",
    }
    # Normalize the film name to lowercase for consistent searching
    film_name = film_name.lower()
    params = {"keyword": film_name}  # Parameters for the API request

    try:
        response = requests.get(url, headers=headers, params=params, timeout=4)

        # Check if the response is successful
        if response.status_code == 200:
            film_data = response.json()  # Parse the JSON response
            films = film_data.get("films", [])
            return films[0] if films else None
        else:
            logger.error(f"search_film response error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error("Kinopoisk search issue", icon="🚨")
        logger.error(f"search_film error: {e}")


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
            0.0 if mov_vars["rating"] in ["null", None, ""] else float(mov_vars["rating"])
        )
        mov_vars["type"] = get_movie_type(mov_vars)

        return mov_vars

    except Exception as e:
        logger.error(f"data_preparation error: {e}, mov_vars")
        return None


# Saving data in "offered movies" table in DB
def offer_film(new_mov):
    """Searches for information about a film and adds it to the "offered movies" table in the database

    Args:
        new_mov (str): The name of the film to offer
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
        # Convert the message to lowercase for consistency
        error_msg = str(e).lower()

        # Check for specific error codes or messages related to duplicate entries
        if "23505" in error_msg or "duplicate key" in error_msg:
            logger.warning(f"Попытка добавить дубликат: {new_mov}")
        else:
            st.error(f"This is an error: {e}", icon="🚨")
            logger.error(f"offer_film error: {e}")


# Movie form function
def movie_form():
    submitted = st.session_state.get("submitted", False)

    # If the form has not been submitted, display the input form for suggesting a movie
    if not submitted:
        with st.form("add_movie_form"):
            # Input field for the movie name
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
            # .strip() is used to remove any leading or trailing whitespace from the movie name
            if send and mov.lower().strip():
                # state is used to track the submission status and any inappropriate words
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
    Movie processing: search + formatting

    Args:
        name: Name of the movie

    Returns:
        Prepared data for the database or None
    """

    raw_data = search_film(movie_name)

    if raw_data is not None:
        mov_data = data_preparation(raw_data)

        if mov_data is not None:
            del mov_data["url"]  # Remove the 'url' key as it's not needed for database insertion

        return mov_data

    return None
