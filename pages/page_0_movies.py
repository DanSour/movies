import streamlit as st
from gotrue.errors import AuthApiError

from appearance import create_checkboxes, links_to_watch, movie_form
from data_processing import (
    filter_dataframe,
    load_data,
    logger,
)

logger.add(
    "logs/data_processing/debug.log",
    rotation="100 MB",
    compression="zip",
    level="DEBUG",
)
def main():

    # st.cache_data.clear()
    # Show the page title and description.
    st.set_page_config(
        page_title="Список фильмов",
        # initial_sidebar_state="collapsed",
        page_icon="🎬",
        menu_items={
            "About": "# This is an *extremely* cool app! \n\
                        Как же я *** это делать... \n\
    Разработчик - [DanSour](http://github.com/DanSour)"
        },
    )

    st.title("🎥 Смотреть онлайн бесплатно")
    st.subheader(
        "Тут можно выбирать что ты хочешь сегодня смотреть 🤩 👀 ",
        divider="violet",
    )
    st.write(
        ":violet-background[это все произведения, "
        "которые я хочу посмотреть когда-нибудь...]"
    )

    df = load_data()
    movie_form()
    selected_types = create_checkboxes()
    
    # Добавляем слайдер для выбора года
    years = st.slider("Годы", min_value=1950, max_value=2030, value=(1954, 2010))

    # Фильтрация DataFrame
    df_filtered = filter_dataframe(df, selected_types, years)

    # Объединяем все списки жанров в один,
    # преобразуем объединенный список в множество для получения уникальных жанров
    # и удаляем заданные жанры из множества уникальных жанров
    unique_genres = {
        genre for sublist in df_filtered["genres"] for genre in sublist.split(", ")
    } - {"аниме", "мультфильм"}

    # Теперь можно использовать unique_genres в multiselect
    genres = st.multiselect(
        "genres",
        sorted(unique_genres),
        placeholder="Жанры",
        label_visibility="collapsed",
    )

    if genres:
        df_filtered = df_filtered[
            df_filtered["genres"].apply(
                lambda x: all(genre in x.split(", ") for genre in genres)
            )
        ]

    st.write("Посмотреть постер - :red[дважды] на него нажмай")

    # Показать данные на экране через st.dataframe
    st.dataframe(
        df_filtered,
        use_container_width=True,
        # форматирование датафрейма
        column_config={
            "name": st.column_config.TextColumn(
                "Название",
                width="medium",
            ),
            "posterUrl": st.column_config.ImageColumn(
                "Постер",
            ),
            "year": st.column_config.NumberColumn(
                "Год",
                format="%d",
            ),
            "genres": st.column_config.ListColumn(
                "Жанры",
                width="medium",
            ),
            "rating": st.column_config.NumberColumn(
                "Рейтинг",
                # width ='small',
                help="Рейт на Кинопоиску",
            ),
            "length": st.column_config.TimeColumn(
                "Длительность",
                format="HH:mm",
            ),
            # width ='small',
            "type": st.column_config.TextColumn(
                "Формат",
            ),
        },
        hide_index=True,
    )

    st.button("Где посмотреть", key="wherewatch")
    placeholder = st.empty()

    # Инициализация состояния
    if "displayed_text" not in st.session_state:
        st.session_state.displayed_text = ""

    # Показываем сохранённый текст при наличии
    if st.session_state.displayed_text:
        placeholder.markdown(st.session_state.displayed_text)

    if st.session_state.wherewatch:
        # Сброс предыдущего текста
        st.session_state.displayed_text = ""
        placeholder.empty()

        # Анимация ввода
        st.session_state.displayed_text = links_to_watch(placeholder)


if __name__ == "__main__":
    try:
        main()
    except ValueError as ve:
        logger.error(f"Ошибка ValueError в main: {ve}")
    except TypeError as te:
        logger.error(f"Ошибка TypeError в main: {te}")
    # Можно добавлять конкретные исключения по мере необходимости
    # except SomeSpecificException as se:
    #     logger.error(f"Ошибка SomeSpecificException в main: {se}")
    except AuthApiError as e:
        # Обработка ошибки авторизации
        logger.error(f"Ошибка авторизации: {e}")
        st.sidebar.error("Неверный email или пароль ❌")
    except Exception as e:
        logger.error(f"Неожиданная ошибка в main: {e}")

