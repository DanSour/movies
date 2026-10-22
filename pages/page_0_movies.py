import streamlit as st

from appearance import create_checkboxes, links_to_watch
from scripts.data_processing import filter_dataframe, logger
from scripts.scripts_movies import load_movies, movie_form

# logger.add(
#     "logs/data_processing/debug.log",
#     rotation="100 MB",
#     compression="zip",
#     level="DEBUG",
# )


def main():

    st.cache_data.clear()
    # Show the page title and description.
    st.set_page_config(
        page_title="Список фильмов",
        # initial_sidebar_state="expanded",
        initial_sidebar_state="collapsed",
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

    movie_form()

    # slider for years filter
    years = st.slider("Годы", min_value=1950, max_value=2030, value=(1990, 2020))
    selected_types = create_checkboxes()

    st.write("Посмотреть постер - :red[дважды] на него нажмай")

    df = load_movies()

    # DataFrame filtration
    df_filtered = filter_dataframe(df, selected_types, years)

    # Combine all genres into one list,
    # convert into a set of unique genres
    # and remove the specified genres from the set
    unique_genres = {
        genre for sublist in df_filtered["genres"] for genre in sublist.split(", ")
    } - {"аниме", "мультфильм"}

    # using unique_genres in multiselect
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

    # Show data with st.dataframe
    st.dataframe(
        df_filtered,
        width='stretch',
        # dataframe formatting
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
                help="Рейт на Кинопоиску",
            ),
            "length": st.column_config.TimeColumn(
                "Длительность",
                format="HH:mm",
            ),
            "type": st.column_config.TextColumn(
                "Формат",
            ),
        },
        hide_index=True,
    )

    st.button("Где посмотреть", key="wherewatch")
    placeholder = st.empty()

    # Check if 'displayed_text' is in session state, if not, initialize it
    if "displayed_text" not in st.session_state:
        st.session_state.displayed_text = ""

    # Check if 'wherewatch' is in session state, if not, initialize it
    if st.session_state.displayed_text:
        placeholder.markdown(st.session_state.displayed_text)

    if st.session_state.wherewatch:
        # If the button is clicked, clear the placeholder and reset the displayed text
        st.session_state.displayed_text = ""
        placeholder.empty()

        # Animation for loading
        st.session_state.displayed_text = links_to_watch(placeholder)


if __name__ == "__main__":
    try:
        main()
    except ValueError as ve:
        logger.error(f"ValueError in main: {ve}")
        st.error(f"ValueError in main: {ve}")
    except TypeError as te:
        logger.error(f"TypeError in main: {te}")
        st.error(f"TypeError in main: {te}")
    # We can add more specific exception handling as needed
    except Exception as e:
        logger.error(f"This is an error in main: {e}")
        st.error(f"This is an error in main: {e}", icon="🚨")
