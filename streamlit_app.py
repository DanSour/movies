import streamlit as st
import pandas as pd
import time
from search_keywords import *
from data_processing import *
from appearance import *

st.cache_data.clear()
# Show the page title and description.
st.set_page_config(page_title="Список фильмов", 
                   page_icon="🎬", 
                   menu_items={
                       'About': "# This is an *extremely* cool app! \n\
                       Как же я заебался это делать..."
                   }
                )

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df = pd.read_csv("data/movies.csv", sep='\t')
    # st.write(df.iloc[0])

    return df


st.title("🎥 Смотреть онлайн бесплатно")
st.subheader("Вот тут и будем выбирать что мы будем сегодня смотреть  🤩 👀 ", divider='violet')
st.write(":violet-background[это все произведения которые я хочу посмотреть когда-нибудь...]")

df = load_data()

if "disabled" not in st.session_state:
    st.session_state.disabled = False
    st.session_state.new_mov = ""

def on_change():
    st.session_state.disabled = True
    st.session_state.new_mov = ""

def enable_input():
    st.session_state.disabled = False

text_input = st.text_input(
    "Введите текст",
    label_visibility='collapsed',
    placeholder='Предложить еще',
    key="new_mov",
    on_change=on_change,
    disabled=st.session_state.disabled
)
# включает кнопку для повторного открытия доступа к полю ввода
if st.session_state.disabled:
    st.button("Разблокировать поле ввода", on_click=enable_input, disabled=not st.session_state.disabled)

# st.text_input("New-mov", label_visibility='collapsed', placeholder='Добавить новый', key='new_mov')
if text_input:
    # st.info('Спасибо за предложение!!!')
    st.success('Спасибо за предложение!!!', icon="✅")
    # add_film(st.session_state.new_mov)
    # updated_df = add_film(st.session_state.new_mov, df)
    # if updated_df is not None:
    #     df = updated_df
        # # Очистка текстового поля после добавления фильма
        # st.session_state.new_mov = ' '
        # Флажок для перезагрузки данных
        # st.experimental_rerun()


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


def stream_data():
    text = '''
    [reyohoho.github.io/reyohoho](https://reyohoho.github.io/reyohoho) \n
    [reyohoho.serv00.net](https://reyohoho.serv00.net) \n
    [reyohoho.vercel.app](https://reyohoho.vercel.app) \n
    [reyohoho.surge.sh](https://reyohoho.surge.sh) \n
    '''
    return text

if st.button("Где посмотреть"):
    sleep = 0.03
    placeholder = st.empty()
    full_text = ""
    for char in stream_data():
        if char == '(':
            sleep = 0
        elif char == '[':
            sleep = 0.03

        full_text += char
        placeholder.markdown(full_text)
        time.sleep(sleep)

# streamlit run streamlit_app.py --server.enableCORS false --server.enableXsrfProtection false

