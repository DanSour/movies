import streamlit as st
import pandas as pd

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
        MOVIE: col1.checkbox("Фильм :green[Фильм] :violet[Фильм] ", key='movie'),
        CARTOON: col1.checkbox(":rainbow[Мульт]", key='cartoon'),
        ANIME: col1.checkbox(":rainbow-background[Аниме] :cherry_blossom: ", value=True, key='anime'),
        SERIES: col2.checkbox(":orange-background[Сериал] 🎬", key='series'),
        CARTOON_SERIES: col2.checkbox(":blue[Мульт]-:orange[сериал]", key='cartoon_series'),
        ANIME_SERIES: col2.checkbox(":red[Аниме]-:violet-background[сериал] ㊙️", key='anime_series')
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

