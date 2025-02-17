import streamlit as st

from appearance import create_checkboxes, links_to_watch
from data_processing import logger, load_data, filter_dataframe, add_film

logger.add(
    "logs/data_processing/debug.log",
    rotation="100 MB",
    compression="zip",
    level="DEBUG",
)

# st.cache_data.clear()
# Show the page title and description.
st.set_page_config(
    page_title="Список фильмов",
    page_icon="🎬",
    menu_items={
        "About": "# This is an *extremely* cool app! \n\
                       Как же я заебался это делать... \n\
Чел который это сделал - [DanSour](http://github.com/DanSour)"
    },
)


def main():
    st.title("🎥 Смотреть онлайн бесплатно")
    st.subheader(
        "Вот тут и будем выбирать что мы будем сегодня смотреть  🤩 👀 ",
        divider="violet",
    )
    st.write(
        ":violet-background[это все произведения, "
        "которые я хочу посмотреть когда-нибудь...]"
    )
    df = load_data()

    if "disabled" not in st.session_state:
        st.session_state.disabled = False
    if "placeholder" not in st.session_state:
        st.session_state.placeholder = "Предложить"

    def on_change():
        st.session_state.disabled = True
        st.session_state.placeholder = st.session_state.new_mov
        # Функция добавления нового фильма в базу данных
        if st.session_state.new_mov not in ["хуй", "пенис", "пизда"]:
            add_film(st.session_state.new_mov)
        else:
            pass

    def enable_input():
        st.session_state.disabled = False
        st.session_state.placeholder = "Предложить"

    st.text_input(
        "текст",
        label_visibility="collapsed",
        placeholder=st.session_state.placeholder,
        key="new_mov",
        on_change=on_change,
        disabled=st.session_state.disabled,
    )
    # включает кнопку для повторного открытия доступа к полю ввода
    if st.session_state.disabled:
        if st.session_state.placeholder.lower() in ["хуй", "пенис", "пизда"]:
            st.error(
                f"Себе {st.session_state.placeholder} порекомендуй, клоун 👊😡",
                icon="🤡",
            )
        else:
            # st.info('Спасибо за предложение!!!')
            st.success("Спасибо за предложение!!", icon="✅")
            st.button(
                "Предложить еще",
                on_click=enable_input,
                disabled=not st.session_state.disabled,
            )

    col1, col2 = st.columns(2)
    selected_types = create_checkboxes(col1, col2)
    # Добавляем слайдер для выбора года
    years = st.slider("Годы", min_value=1950,
                      max_value=2030, value=(1954, 2010))

    # Фильтрация DataFrame
    df_filtered = filter_dataframe(df, selected_types, years)

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
            "img": st.column_config.ImageColumn(
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
    except Exception as e:
        # Ловим все остальные исключения для предотвращения сбоя приложения
        logger.error(f"Неожиданная ошибка в main: {e}")

# streamlit run streamlit_app.py --server.enableCORS false --server.enableXsrfProtection false
