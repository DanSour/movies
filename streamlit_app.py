import streamlit as st

st.set_page_config(
    initial_sidebar_state="collapsed"
)

pg = st.navigation([
    st.Page("pages/page_0_movies.py", title="Фильмы", default=True),
    st.Page("pages/page_1_games.py", title="Игры"),
    st.Page("pages/page_2_admin_panel.py", title="Admin panel"),
])
pg.run()


# streamlit run streamlit_app.py
# --server.enableCORS false --server.enableXsrfProtection false
