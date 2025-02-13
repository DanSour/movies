import pandas as pd


def get_movie_type(movie_vars):
    genres = set(movie_vars.get('genres', '').lower().split(', '))
    movie_type = movie_vars.get('type', '')

    # Определение типа произведения на основе жанров и типа
    if 'аниме' in genres:
        if movie_type in ['TV_SERIES', 'MINI_SERIES']:
            return 'Аниме-сериал'
        elif movie_type == 'FILM':
            return 'Мульт'
    elif 'мультфильм' in genres:
        if movie_type in ['TV_SERIES', 'MINI_SERIES']:
            return 'Мульт-сериал'
        elif movie_type == 'FILM':
            return 'Мульт'
    
    # Определение типа произведения по типу (если жанры не помогли)
    type_mapping = {
        'FILM': 'Фильм',
        'TV_SERIES': 'Сериал',
        'MINI_SERIES': 'Сериал'
    }
    
    return type_mapping.get(movie_type, 'Неизвестный тип')


def movie_preparation(mov_vars):
    
    keys_to_keep = ["nameRu", "posterUrl", "year", "genres", "rating", "filmLength", "type"]
    mov_vars = {k: v for k, v in mov_vars.items() if k in keys_to_keep} 

    mov_vars['genres'] = ', '.join([item['genre'] for item in mov_vars['genres']])
    mov_vars['posterUrl'] = f'<img src={mov_vars["posterUrl"]} alt="img" width="100" />'
    # mov_vars['posterUrl'] = f'![|100]({(mov_vars["posterUrl"])})'
    
    mov_vars['type'] = get_movie_type(mov_vars)
    
    mov_data = pd.DataFrame([mov_vars], columns=keys_to_keep)
    mov_data = mov_data.to_markdown(index=False)
    mov_data = mov_data.split('\n')[2:]
    mov_data = mov_data[0]
    return mov_data