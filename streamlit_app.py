import streamlit as st
import pandas as pd
from search_keywords import film_json
from data_preparation import *
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
# @st.cache_data
def load_data():
    # df = pd.read_csv("data/movies_genres_summary.csv")
    df = pd.read_csv("data/movies.csv", sep='\t')
    # df['img'] = df['img'].apply(lambda x: st.markdown(
        # x, f"[![Click me]({x})]", unsafe_allow_html=False,
    # )
    # df['img'] = df['img'].apply(
    #     lambda x: f'{x.split("src=")[1].split(" ")[0].strip("<>")}'
    # )
    # df['img'] = df['img'].apply(lambda x: st.image(x, width=10, use_container_width=True))

    return df


st.title("🎥 Смотреть онлайн бесплатно")
# st.subheader("🎥 Смотреть онлайн бесплатно", divider='blue')
st.subheader("Вот тут и будем выбирать что мы будем сегодня смотреть  🤩 👀 ", divider='violet')
st.write(":violet-background[это все произведения которые я хочу посмотреть когда-нибудь...]")
df = load_data()

st.text_input("New-mov", label_visibility='collapsed', placeholder='Добавить новый', key='new_mov')
if st.session_state.new_mov:
    try:
        st.error('Подожди, еще не сделана функция', icon="🚨")
        # mov_vars = film_json(st.session_state.new_mov.lower())
        # if mov_vars == None:
# надо будет где то убрать этот эррор или тут
            # st.error('Не найдено', icon="🚨")

        # mov_data = movie_preparation(mov_vars)
        # st.success('База данных обновлена!', icon="✅")
        # st.write(mov_data)

        # st.write(st.session_state.new_mov)
    except Exception as e:
        st.error(f'This is an error: {e}', icon="🚨")

col1, col2 = st.columns(2)
selected_types = create_checkboxes(col1, col2)
# Добавляем слайдер для выбора года
years = st.slider("Годы", min_value=1950, max_value=2030, value=(1954, 2010))
# Фильтрация DataFrame
df_filtered = filter_dataframe(df, selected_types, years)
st.write('Посмотреть постер - :red[дважды] на него нажмай')
# Display the data as a table using `st.dataframe`.
st.dataframe(
    df_filtered,
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

df_html = pd.read_csv("data/movies_html.csv", sep='\t')
df_filtered_html = filter_dataframe(df_html, selected_types, years)
st.write(df_filtered_html.to_html(escape=False, index=False), unsafe_allow_html=True)

# def stream_data():
#     import time

#     text = '''
#     [reyohoho.github.io/reyohoho]('reyohoho.github.io/reyohoho')\n
#     [reyohoho.serv00.net]('reyohoho.serv00.net')\n
#     [reyohoho.vercel.app]('reyohoho.vercel.app')\n
#     [reyohoho.surge.sh]('reyohoho.surge.sh')\n
#     '''
#     sleep = .03
#     for char in text:
#         if char == '(':
#             sleep = 0
#         elif char == '[':
#             sleep = 0.03
#         yield char + ""
#         time.sleep(sleep)
    
# # Постепенный вывод ссылок в формате md
# if st.button("Где посмотреть"):
#     st.write_stream(stream_data)
import streamlit as st
import time

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
# if st.button("Где посмотреть", key="unique_key"):
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