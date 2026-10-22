import streamlit as st
from supabase_auth.errors import AuthApiError

from scripts.data_processing import authenticate, handle_media_operation, logger


def admin_callback():
    handle_media_operation(
        media_type=st.session_state.key_type,
        action_type=st.session_state.key_function,
        name=st.session_state.key_name,
        supabase_client=st.session_state.auth["client"],
    )
    return


# Checking if the user is admin
def main():

    admin = st.session_state.get("admin", False)

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

            submitted = st.form_submit_button("Submit")
            if submitted:
                st.session_state.auth = authenticate(username, password)
                if st.session_state.auth["response"]:
                    st.session_state.admin = True
                    st.rerun()
                else:
                    st.error("Неверный ключ")

    if admin:
        with st.form("add_media_form"):

            col1, col2 = st.columns(2, gap="small")
            with col1:
                st.segmented_control(
                    "Type",
                    options=["🎬 Movie", "🎮 Game"],
                    selection_mode="single",
                    default="🎬 Movie",
                    key="key_type",
                )

            with col2:
                st.segmented_control(
                    "Function",
                    options=["➕ Insert", "🗑️ Delete"],
                    selection_mode="single",
                    default="➕ Insert",
                    key="key_function",
                )

            st.text_input(
                " ",
                label_visibility="collapsed",
                key="key_name",
            )

            st.form_submit_button(
                "Submit",
                on_click=admin_callback,
            )


if __name__ == "__main__":
    try:
        main()
    except ValueError as ve:
        logger.error(f"Ошибка ValueError в main: {ve}")
    except TypeError as te:
        logger.error(f"Ошибка TypeError в main: {te}")
    # We can add more specific exception handling as needed
    except AuthApiError as e:
        # Handle authentication errors specifically
        logger.error(f"Ошибка авторизации: {e}")
        st.error("Неверный email или пароль ❌")
    except Exception as e:
        logger.error(f"Неожиданная ошибка в main: {e}")
