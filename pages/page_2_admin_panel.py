import streamlit as st
from gotrue.errors import AuthApiError

from data_processing import admin_access, authenticate, logger

logger.add(
    "logs/data_processing/debug.log",
    rotation="100 MB",
    compression="zip",
    level="DEBUG",
)


# Проверка, является ли пользователь владельцем
def main():

    # if "admin" not in st.session_state:
    #     st.session_state.admin = False
    admin = st.session_state.get("admin", False)

    # # Проверяем, были ли уже отправлены данные
    # if "form_data" not in st.session_state:
    #     with st.form("my_form"):
    #         name = st.text_input("Введите имя")
    #         submitted = st.form_submit_button("Отправить")
    #         if submitted:
    #             st.session_state.form_data = name  # Сохраняем данные
    # else:
    #     st.write("Спасибо! Вы ввели:", st.session_state.form_data)

    def admin_add_film():
        admin_access(
            movie=st.session_state.mov,
            st_supabase_client=st.session_state.auth["client"],
            key_word=st.session_state.key_word,
        )

    # if not st.session_state.admin:
    if not admin:
        with st.form("admin_form", enter_to_submit=True):
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

            # if st.form_submit_button("Submit"):
            submitted = st.form_submit_button("Submit")
            if submitted:
                st.session_state.auth = authenticate(username, password)
                if st.session_state.auth["response"]:
                    st.session_state.admin = True
                    st.rerun()
                else:
                    st.error("Неверный ключ")

    # if st.session_state.admin:
    if admin:
        with st.form("add_mov"):

            st.segmented_control(
                "Func",
                ["insert", "delete"],
                selection_mode="single",
                default="insert",
                key="key_word",
            )
            # Показываем поле ввода текста только владельцу
            st.text_input(
                " ",
                label_visibility="collapsed",
                key="mov",
            )

            st.form_submit_button(
                "Submit",
                on_click=admin_add_film,
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
        st.error("Неверный email или пароль ❌")
    except Exception as e:
        logger.error(f"Неожиданная ошибка в main: {e}")
