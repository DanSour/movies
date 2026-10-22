import pandas as pd
import streamlit as st
from howlongtobeatpy import HowLongToBeat
from loguru import logger
from st_supabase_connection import execute_query

from scripts.data_processing import init_supabase_client


# Load the data from a SupabaseConnection. We're caching this so
# it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_games():
    """
    Data uploading

    Returns:
        pd.DataFrame: games table from DB
    """
    st_supabase_client = init_supabase_client()
    request = execute_query(
        st_supabase_client.table("games").select("*").order("name"), ttl=0
    )
    return pd.DataFrame(request.data)


def process_game(game_name: str) -> dict:
    """
    Full game processing: search + formatting

    Args:
        name: Name of the game

    Returns:
        Prepared data for DB or None
    """
    try:
        if game_name.isdigit():
            game_data = HowLongToBeat().search_from_id(int(game_name))
            game_vars = vars(game_data)
        else:
            results = HowLongToBeat(0.0).search(game_name, similarity_case_sensitive=False)  # for search by game_name
            if len(results) > 0:
                game = results[0]
                game_vars = vars(game)

            keys_to_keep = [
                "game_name",
                "game_image_url",
                "release_world",
                "main_story",
                "main_extra",
                "completionist",
                "profile_platforms",
            ]
            game_vars = {k: game_vars.get(k, None) for k in keys_to_keep}

            game_vars["profile_platforms"] = ", ".join(
                [pl for pl in game_vars["profile_platforms"]]
            )

            game_vars["name"] = game_vars.pop("game_name")
            game_vars["posterUrl"] = game_vars.pop("game_image_url")
            game_vars["year"] = game_vars.pop("release_world")
            game_vars["platforms"] = game_vars.pop("profile_platforms")

            return game_vars

        return None

    except Exception as e:
        st.error("HowLongToBeat search issue", icon="🚨")
        logger.error(f"process_game error: {e}")
        return None
