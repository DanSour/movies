import pandas as pd
import streamlit as st
from loguru import logger
from st_supabase_connection import SupabaseConnection, execute_query


def init_supabase_client():
    if "st_supabase_client" not in st.session_state:
        try:
            st.session_state.st_supabase_client = st.connection(
                name="SupabaseConnection",
                type=SupabaseConnection,
                ttl=20,
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            st.error(f"This is an error: {e}", icon="🚨")
    return st.session_state.st_supabase_client


def authenticate(username: str, password: str) -> dict:
    """User authentication

    Args:
        username (str): Email registered for database modification
        password (str): Registered password

    Returns:
        dict: Dictionary containing connection success status and the Supabase client
    """
    client = init_supabase_client()
    response = client.auth.sign_in_with_password(
        {"email": username, "password": password}
    )
    return {"response": bool(response), "client": client}


def filter_dataframe(df, selected_types, years):
    """Filters a DataFrame by selected content types and year range

    Args:
        df (pd.DataFrame): The input DataFrame
        selected_types (list): List of selected content types
        years (tuple): Year range (min_year, max_year)

    Returns:
        pd.DataFrame: The filtered DataFrame
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


def process_media_by_type(table: str, name: str) -> dict:
    from scripts.scripts_games import process_game
    from scripts.scripts_movies import process_movie

    """
    Process media based on its type

    Args:
        table: Table name (movies/games)
        name: Media name

    Returns:
        Prepared data or None
    """
    if table == "movies":
        return process_movie(name)
    elif table == "games":
        return process_game(name)
    else:
        logger.error(f"Unknown table type: {table}")
        return None


def execute_db_operation(supabase_client, table: str, action: str, data: dict):
    """
    Executes a database operation based on the specified action.

    Args:
        supabase_client: The Supabase client instance.
        table (str): The name of the table to perform the operation on.
        action (str): The type of operation to perform ("insert" or "delete").
        data (dict): The data to be used in the operation.

    Raises:
        ValueError: If the specified action is unsupported.
        Exception: For any other errors encountered during execution.
    """
    try:
        if action == "insert":
            execute_query(supabase_client.table(f"{table}").insert(data), ttl=0)

        elif action == "delete":
            action = "delet"
            executed = execute_query(
                supabase_client.table(f"{table}").delete().eq("name", data["name"]),
                ttl=0,
            )
            if executed.data == []:
                logger.info(f'"{data["name"]}" not in DB')
                st.warning(f"⚠️ '{data['name']}' not in DB")
                return

        logger.success(f"Successfully {action}ed: {data['name']}")
        st.success(f"✅ Successfully {action}ed: {data['name']}")
        return

    except ValueError as ve:
        logger.error(f"Unsupported operation '{action}' caused ValueError: {ve}")
        st.error(f"Unsupported operation: {action}")
    except Exception as e:
        # Convert the message to lowercase for consistency
        error_msg = str(e).lower()

        # Check for error code 23505 or keywords "duplicate"
        if "23505" in error_msg or "duplicate" in error_msg:
            logger.warning(f"Duplicate: {data["name"]}")
            st.warning("⚠️ Duplicate")
        else:
            logger.error(f"execute_db_operation error: {e}")
            st.error(f"execute_db_operation error: {e}", icon="🚨")


def handle_media_operation(
    media_type: str, action_type: str, name: str, supabase_client
):
    """
    Process media: find, prepare data, and perform the operation.

    Args:
        media_type: 🎬 Movie / 🎮 Game
        action_type: ➕ Insert / 🗑️ Delete
        name: Media name
        supabase_client: Supabase client instance

    """
    MEDIA_TABLES = {"🎬 Movie": "movies", "🎮 Game": "games"}

    ACTIONS = {"➕ Insert": "insert", "🗑️ Delete": "delete"}

    table = MEDIA_TABLES.get(media_type)
    action = ACTIONS.get(action_type)

    if not table:
        st.error(f"Invalid media type: {media_type}")
        return

    if not action:
        st.error(f"Invalid action: {action_type}")
        return

    try:
        # processing media (search + preparation)
        data = process_media_by_type(table, name)

        if data is None:
            message = f"{media_type} not found: '{name}'"
            st.info(message)
            logger.warning(message)
            return

        # operate in DB (insert/delete)
        execute_db_operation(supabase_client, table, action, data)

        return

    except Exception as e:
        st.error(f"handle_media_operation error: {e}", icon="🚨")
        logger.error(f"handle_media_operation error: {e}")
