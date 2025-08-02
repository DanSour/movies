import time
import streamlit as st
from data_processing import add_film


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
                    add_film(mov)
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


def create_checkboxes():
    col1, col2 = st.columns(2)
    """Создает чекбоксы для выбора типов контента в двух колонках.

    Args:
        col1 (st.container): Первая колонка Streamlit.
        col2 (st.container): Вторая колонка Streamlit.

    Returns:
        list: Список выбранных типов контента.
    """
    # Константы для названий типов контента
    MOVIE = "Фильм"
    CARTOON = "Мульт"
    ANIME = "Аниме"
    SERIES = "Сериал"
    CARTOON_SERIES = "Мульт-сериал"
    ANIME_SERIES = "Аниме-сериал"

    # Словарь для сопоставления ключей чекбоксов с названиями типов контента
    checkboxes = {
        MOVIE: col1.checkbox("Фильм :green[Фильм] :violet[Фильм]", value=True),
        CARTOON: col1.checkbox(":rainbow[Мульт]"),
        ANIME: col1.checkbox(":rainbow-background[Аниме] :cherry_blossom: "),
        SERIES: col2.checkbox(":orange-background[Сериал] 🎬"),
        CARTOON_SERIES: col2.checkbox(":blue[Мульт]-:orange[сериал]"),
        ANIME_SERIES: col2.checkbox(":red[Аниме]-:violet-background[сериал] ㊙️"),
    }
    # Создаем список выбранных типов контента
    selected_types = [
        content_type for content_type, is_selected in checkboxes.items() if is_selected
    ]
    return selected_types


def stream_data():
    text = """
    [reyohoho.github.io/reyohoho](https://reyohoho.github.io/reyohoho) \n
    [reyohoho.serv00.net](https://reyohoho.serv00.net) \n
    [reyohoho.vercel.app](https://reyohoho.vercel.app) \n
    [reyohoho.surge.sh](https://reyohoho.surge.sh) \n
    """
    return text


def links_to_watch(placeholder):
    """Выводит на экран текст из stream_data()

    Args:
        placeholder: пустой placeholder

    Returns:
        placeholder: заполненный текстом placeholder
    """
    # Анимация ввода
    sleep = 0.03
    full_text = ""
    for char in stream_data():
        if char == "]":
            sleep = 0
        elif char == "[":
            sleep = 0.03

        full_text += char
        placeholder.markdown(full_text)
        time.sleep(sleep)
    return full_text
