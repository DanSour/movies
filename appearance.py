import time


def create_checkboxes(col1, col2):
    """Создает чекбоксы для выбора типов контента в двух колонках.

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
        MOVIE: col1.checkbox("Фильм :green[Фильм] :violet[Фильм] "),
        CARTOON: col1.checkbox(":rainbow[Мульт]", value=True),
        ANIME: col1.checkbox(":rainbow-background[Аниме] :cherry_blossom: "),
        SERIES: col2.checkbox(":orange-background[Сериал] 🎬"),
        CARTOON_SERIES: col2.checkbox(":blue[Мульт]-:orange[сериал]"),
        ANIME_SERIES: col2.checkbox(":red[Аниме]-:violet-background[сериал] ㊙️"),
    }
    # Создаем список выбранных типов контента
    selected_types = [
        content_type for content_type, is_selected in checkboxes.items() if is_selected
    ]
    return selected_types


def stream_data():
    text = """
    [reyohoho.github.io/reyohoho](https://reyohoho.github.io/reyohoho) \n
    [reyohoho.serv00.net](https://reyohoho.serv00.net) \n
    [reyohoho.vercel.app](https://reyohoho.vercel.app) \n
    [reyohoho.surge.sh](https://reyohoho.surge.sh) \n
    """
    return text


def links_to_watch(placeholder):
    """Выводит на экран текст из stream_data()

    Args:
        placeholder: пустой placeholder

    Returns:
        placeholder: заполненный текстом placeholder
    """
    # Анимация ввода
    sleep = 0.03
    full_text = ""
    for char in stream_data():
        if char == "]":
            sleep = 0
        elif char == "[":
            sleep = 0.03

        full_text += char
        placeholder.markdown(full_text)
        time.sleep(sleep)
    return full_text
