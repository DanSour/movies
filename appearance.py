import streamlit as st
import pandas as pd
import time

def create_checkboxes(col1, col2):
    """
    Создает чекбоксы для выбора типов контента в двух колонках.
    
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
        MOVIE: col1.checkbox("Фильм :green[Фильм] :violet[Фильм] ") , # key='movie'),
        CARTOON: col1.checkbox(":rainbow[Мульт]", value=True) , # key='cartoon'),
        ANIME: col1.checkbox(":rainbow-background[Аниме] :cherry_blossom: ") , # key='anime'),
        SERIES: col2.checkbox(":orange-background[Сериал] 🎬") , # key='series'),
        CARTOON_SERIES: col2.checkbox(":blue[Мульт]-:orange[сериал]") , # key='cartoon_series'),
        ANIME_SERIES: col2.checkbox(":red[Аниме]-:violet-background[сериал] ㊙️") , # key='anime_series')
    }
    # Создаем список выбранных типов контента
    selected_types = [content_type for content_type, is_selected in checkboxes.items() if is_selected]
    return selected_types


def filter_dataframe(df, selected_types, years):
    """
    Фильтрует DataFrame по выбранным типам контента и диапазону лет.
    
    Args:
        df (pd.DataFrame): Исходный DataFrame.
        selected_types (list): Список выбранных типов контента.
        years (tuple): Диапазон лет (min_year, max_year).
        
    Returns:
        pd.DataFrame: Отфильтрованный DataFrame.
    """
    try:
        year_filter = df["year"].between(years[0], years[1])
        if selected_types:
            type_filter = df["type"].isin(selected_types)
            return df[year_filter & type_filter]
        else:
            return df[year_filter]
    except KeyError:
        st.error("Колонка 'type' или 'year' не найдена в DataFrame.")
        return pd.DataFrame()


def stream_data():
    text = '''
    [reyohoho.github.io/reyohoho](https://reyohoho.github.io/reyohoho) \n
    [reyohoho.serv00.net](https://reyohoho.serv00.net) \n
    [reyohoho.vercel.app](https://reyohoho.vercel.app) \n
    [reyohoho.surge.sh](https://reyohoho.surge.sh) \n
    '''
    return text


def links_to_watch(placeholder):
    '''
    Выводит на экран текст из stream_data()

    args:
        placeholder: пустой placeholder
    
    Returns:
        placeholder: заполненный текстом placeholder
    '''
    # Анимация ввода
    sleep = 0.03
    full_text = ""
    for char in stream_data():
        if char == ']':
            sleep = 0
        elif char == '[':
            sleep = 0.03

        full_text += char
        placeholder.markdown(full_text)
        time.sleep(sleep)
    return full_text