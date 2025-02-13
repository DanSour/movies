import pandas as pd
from loguru import logger
import requests
import streamlit as st

logger.add('logs/data_processing/debug.log', rotation='100 MB', compression='zip', level='DEBUG')


def data_load():
    '''
    import streamlit as st
    from st_supabase_connection import SupabaseConnection

    # Initialize connection.
    conn = st.connection("supabase", type=SupabaseConnection)

    # Perform query.
    rows = conn.query("*", table="mytable", ttl="10m").execute()

    # Print results.
    for row in rows.data:
    st.write(f"{row['name']} has a :{row['pet']}:")
    '''
    return
def get_movie_type(movie_vars):
    """
    Определяет тип произведения (фильм, сериал, аниме и т.д.) на основе жанров и типа.

    :param movie_vars: Словарь с информацией о произведении (жанры, тип).
    :return: Тип произведения как строка.
    """
    try:
        # Нормализация входных данных
        genres = set((movie_vars.get('genres', '') or '').lower().split(', '))
        movie_type = movie_vars.get('type', '') # .upper()

        # Маппинг типов по умолчанию
        type_mapping = {
            'FILM': 'Фильм',
            'TV_SERIES': 'Сериал',
            'MINI_SERIES': 'Сериал'
        }

        # Проверка специальных случаев
        if 'аниме' in genres:
            return 'Аниме-сериал' if movie_type in ['TV_SERIES', 'MINI_SERIES'] else 'Мульт'
        elif 'мультфильм' in genres:
            return 'Мульт-сериал' if movie_type in ['TV_SERIES', 'MINI_SERIES'] else 'Мульт'

        # Если специальные случаи не подходят, используем стандартный маппинг
        return type_mapping.get(movie_type, 'Неизвестный тип')

    except AttributeError as e:
        # Логирование конкретной ошибки
        logger.error(f"Ошибка обработки данных в get_movie_type: {e}")
        return 'Неизвестный тип'


def data_preparation(mov_vars)  ->  pd.DataFrame: 
    """
    Превращает json в pd.DataFrame

    :param mov_vars: json с информацией о произведении.
    :return pd.DataFrame: Информация о произведении как DataFrame.
    """
    try:
        keys_to_keep = ["nameRu", "posterUrl", "year", "genres", "rating", "filmLength", "type"]
        mov_vars = {k: v for k, v in mov_vars.items() if k in keys_to_keep} 

        mov_vars['genres'] = ', '.join([item['genre'] for item in mov_vars['genres']])
        # mov_vars['posterUrl'] = f'<img src={mov_vars["posterUrl"]} alt="img" width="100" />'
        
        mov_vars['type'] = get_movie_type(mov_vars)
        
        mov_data = pd.DataFrame([mov_vars], columns=keys_to_keep)
        # mov_data = mov_data.to_markdown(index=False)
        # mov_data = mov_data.split('\n')[2:]
        # mov_data = mov_data[0]
        return mov_data
    except Exception as e:
        logger.error(f'Произошла ошибка data_preparation: {e}')


def film_dict(film_name) -> dict:
    """
    Берет информацию о произведении с сайта ИКНОПОИСК

    :param film_name: str название произведения.
    :return dict: словарь с информацией о произведении.
    """
    url = f'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword?keyword={film_name}'

    # Заголовки запроса
    headers = {
        'X-API-KEY': st.secrets["API_KEY"],
        'Content-Type': 'application/json',
    }

    try:
        response = requests.get(url, headers=headers)

        # Проверяем, успешен ли запрос
        if response.status_code == 200:
            film_data = response.json()  # Преобразуем ответ в JSON
            # if film_data['films'] == []:            
            return film_data['films'][0] if film_data['films'] else None
                # return None
            # else:
                # film_data = film_data['films'][0]
            # return film_data
            # return film_data['films'][0]

        else:
            logger.error(f'Ошибка film_dict: {response.status_code} - {response.text}')
            return None
    except Exception as e:
        # print(f'Произошла ошибка: {e}')
        st.error(f'Произошла ошибка', icon="🚨")
        logger.error(f'Ошибка film_dict: {e}')


# Сохранение данных обратно в CSV файл
def add_film(new_mov, df):
    def save_data(df):
        df.to_csv("data/movies.csv", sep='\t', index=False)

    """
    Ищет информацию о произведении, обновляет файл и при успешном обновлении пишет "УРА"

    Args:
        new_mov (str): название произведения.
    Returns:
    """
    try:
        # st.error('Подожди, еще не сделана функция', icon="🚨")
        mov_vars = film_dict(new_mov.lower())
        if mov_vars == None:
            st.error('Не найдено', icon="🚨")
            logger.info(f'Фильм не найден add_film: {new_mov}')
            return
        
        mov_data = data_preparation(mov_vars)

        # Обновление DataFrame
        df = pd.concat([df, mov_data], ignore_index=True)
        # Сохранение обновленных данных в CSV файл
        save_data(df)
        # Возврат обновленного DataFrame
        return df


    except Exception as e:
        st.error(f'This is an error: {e}', icon="🚨")
        logger.error(f'Ошибка add_film: {e}')
    
        return
