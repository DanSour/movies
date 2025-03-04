import streamlit as st
from gotrue.errors import AuthApiError

from appearance import create_checkboxes, links_to_watch
from data_processing import (
    add_film,
    admin_access,
    authenticate,
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

# st.cache_data.clear()
# Show the page title and description.
st.set_page_config(
    page_title="Список фильмов",
    initial_sidebar_state="collapsed",
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

    def on_change(admin=False):
        st.session_state.disabled = True
        st.session_state.placeholder = st.session_state.new_mov
        # Функция добавления нового фильма в базу данных
        if st.session_state.new_mov.lower() not in ["хуй", "пенис", "пизда"]:
            add_film(st.session_state.new_mov, admin)
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
            st.success("Спасибо за предложение!!", icon="✅")
            st.button(
                "Предложить еще",
                on_click=enable_input,
                disabled=not st.session_state.disabled,
            )

    col1, col2 = st.columns(2)
    selected_types = create_checkboxes(col1, col2)
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

    # Проверка, является ли пользователь владельцем
    with st.sidebar:

        def admin_add_film():
            admin_access(
                movie=mov,
                st_supabase_client=st.session_state.auth["client"],
                key_word=key_word,
            )

        if "admin" not in st.session_state:
            st.session_state.admin = False

        with st.form("my_form"):
            username = st.text_input(
                "Username",
                label_visibility="collapsed",
                placeholder="admin_login",
            )
            password = st.text_input(
                "pswd",
                type="password",
                label_visibility="collapsed",
                placeholder="password",
            )

            if st.form_submit_button("Submit"):
                st.session_state.auth = authenticate(username, password)
                if st.session_state.auth["response"]:
                    st.session_state.admin = True
                else:
                    st.error("Неверный ключ")
        if st.session_state.admin:

            key_word = st.segmented_control(
                "Func", ["insert", "delete"], selection_mode="single", default="insert"
            )
            # Показываем поле ввода текста только владельцу
            mov = st.text_input(
                " ", label_visibility="collapsed", on_change=admin_add_film
            )


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

# streamlit run streamlit_app.py
# --server.enableCORS false --server.enableXsrfProtection false
