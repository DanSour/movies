import requests
import streamlit as st


def film_json(film_name):
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
            if film_data['films'] == []:
# надо будет где то убрать этот эррор или тут 
                st.error('Не найдено', icon="🚨")
            
                # print('Не удалось получить данные')
                return None
            else:
                film_data = film_data['films'][0]
            return film_data

        else:
            print(f'Ошибка: {response.status_code} - {response.text}')
    except Exception as e:
        st.error(f'This is an error: {e}', icon="🚨")
        # print(f'Произошла ошибка: {e}')

if __name__ == '__main__':
    film_name = input('Введите название фильма: ')
    film_data = film_json(film_name)
    if film_data != None:
        print(film_data)
    