import streamlit as st
import pandas as pd
from search_keywords import *
from data_processing import *
from appearance import *
from st_supabase_connection import SupabaseConnection


logger.add('logs/data_processing/debug.log', rotation='100 MB', compression='zip', level='DEBUG')

st.cache_data.clear()
# Show the page title and description.
st.set_page_config(page_title="Список фильмов", 
                   page_icon="🎬", 
                   menu_items={
                       'About': "# This is an *extremely* cool app! \n\
                       Как же я заебался это делать... \n\
Чел который это сделал - [DanSour](http://github.com/DanSour)"
                   }
                )

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df = pd.read_csv("data/movies.csv", sep='\t')
    # 

    return df

def main():
    st.title("🎥 Смотреть онлайн бесплатно")
    st.subheader("Вот тут и будем выбирать что мы будем сегодня смотреть  🤩 👀 ", divider='violet')
    st.write(":violet-background[это все произведения которые я хочу посмотреть когда-нибудь...]")

    df = load_data()


    if "disabled" not in st.session_state:
        st.session_state.disabled = False
        # st.session_state.new_mov = ""
    if 'placeholder' not in st.session_state:
        st.session_state.placeholder = 'Предложить'

    def on_change():
        st.session_state.disabled = True
        st.session_state.placeholder = st.session_state.new_mov
        # Функция добавления нового фильма в удаленную таблицу
        # add_film(st.session_state.new_mov)
        # updated_df = add_film(st.session_state.new_mov, df)

    def enable_input():
        st.session_state.disabled = False
        st.session_state.placeholder = 'Предложить'

    st.text_input(
        "текст",
        label_visibility='collapsed',
        placeholder=st.session_state.placeholder,
        key="new_mov",
        on_change=on_change,
        disabled=st.session_state.disabled
    )
    # включает кнопку для повторного открытия доступа к полю ввода
    if st.session_state.disabled:
        if st.session_state.placeholder.lower() in ['хуй', 'пенис']:
            st.error(f'Себе {st.session_state.placeholder} порекомендуй, клоун 👊😡', icon="🤡")
        else:
            # st.info('Спасибо за предложение!!!')
            st.success('Спасибо за предложение!!', icon="✅")
            st.button("Предложить еще", on_click=enable_input, disabled=not st.session_state.disabled)


    col1, col2 = st.columns(2)
    selected_types = create_checkboxes(col1, col2)
    # Добавляем слайдер для выбора года
    years = st.slider("Годы", min_value=1950, max_value=2030, value=(1954, 2010))

    # Фильтрация DataFrame
    df_filtered = filter_dataframe(df, selected_types, years)


    st.write('Посмотреть постер - :red[дважды] на него нажмай')

    # Показать данные на экране через st.dataframe
    st.dataframe(
        df_filtered,
        # форматирование датафрейма
        column_config={
            "name": st.column_config.TextColumn(
                "Название", 
                width='medium',
            ),
            "img": st.column_config.ImageColumn(
                'Постер', 
            ),
            "year": st.column_config.NumberColumn(
                'Год', 
                format="%d",
            ),
            'genres': st.column_config.ListColumn(
                'Жанры',
                width='medium',
            ),
            "rating": st.column_config.NumberColumn(
                'Рейтинг', 
                # width ='small',
                help='Рейт на Кинопоиску',
            ),
            "length": st.column_config.TimeColumn(
                "Длина",
                format='HH:mm',
            ),
                # width ='small',
            "type": st.column_config.TextColumn(
                "Формат", 
            ),
        },
        hide_index=True,
    )


    st.button("Где посмотреть", key='wherewatch')
    placeholder = st.empty()

    # Инициализация состояния
    if 'displayed_text' not in st.session_state:
        st.session_state.displayed_text = ''

    # Показываем сохранённый текст при наличии
    if st.session_state.displayed_text:
        placeholder.markdown(st.session_state.displayed_text)

    if st.session_state.wherewatch:
        # Сброс предыдущего текста
        st.session_state.displayed_text = ''
        placeholder.empty()
        
        # Анимация ввода
        st.session_state.displayed_text = links_to_watch(placeholder)


if __name__=='__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"Ошибка в main: {e}")

# streamlit run streamlit_app.py --server.enableCORS false --server.enableXsrfProtection false
