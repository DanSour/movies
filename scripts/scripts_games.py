import pandas as pd
import streamlit as st
from st_supabase_connection import execute_query
from scripts.data_processing import init_supabase_client
# from loguru import logger
# import requests


# Load the data from a SupabaseConnection. We're caching this so
# it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_games():
    """Загрузка данных

    Returns:
        pd.DataFrame: таблица фильмов из БД
    """
    st_supabase_client = init_supabase_client()
    request = execute_query(st_supabase_client.table("games").select("*"), ttl=0)

    return pd.DataFrame(request.data)
