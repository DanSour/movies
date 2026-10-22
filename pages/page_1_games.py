import streamlit as st

from scripts.data_processing import logger
from scripts.scripts_games import load_games


def main():

    # Show the page title and description.
    st.set_page_config(
        page_title="Games list",
        initial_sidebar_state="collapsed",
        page_icon="🎮",
    )

    st.title("🎮 Games List")
    st.subheader(
        "♠️♦️🎲 Wanna Play 🎲♣️♥️",
        divider="rainbow",
    )
    # st.write(
    #     ":rainbow-background[Игры, в которые я хочу когда-нибудь поиграть...]"
    # )
    # st.badge("Игры, в которые я хочу когда-нибудь поиграть...", icon=":material/deployed_code:", color="violet")
    st.badge(
        "Игры, в которые я хочу когда-нибудь поиграть...",
        icon=":material/diversity_2:",
        color="violet",
    )
    # st.markdown(":violet-badge[:material/star: Favorite]")

    st.write("Посмотреть постер - :green-badge[дважды] на него нажмай")

    df_games = load_games()

    st.dataframe(
        df_games,
        width="stretch",
        # data formatting
        column_config={
            "name": st.column_config.TextColumn(
                "Название",
                width="medium",
            ),
            "posterUrl": st.column_config.ImageColumn(
                "Постер",
            ),
            "year": st.column_config.NumberColumn(
                "Год",
                format="%d",
                width="small",
            ),
            "main_story": st.column_config.NumberColumn(
                "Время прохождения",
                width="small",
            ),
            "main_extra": st.column_config.NumberColumn(
                "Extra",
                width="small",
            ),
            "completionist": st.column_config.NumberColumn(
                "101%",
                width="small",
            ),
            "platforms": st.column_config.TextColumn(
                "Платформа",
                width="small",
            ),
        },
        hide_index=True,
    )

    expander = st.expander("Additional information", expanded=False)
    expander.write(
        """
        [Киберпанк-игры](https://kanobu.ru/games/collections/kiberpank-igry/)

        Посмотреть игры разработанные компанией Starbreeze Studios

        [FitGirl Repack](https://fitgirl-repack.com/)

        Серия TOM CLANCY’S, SNIPER ELITE
    """
    )


if __name__ == "__main__":
    try:
        main()
    except ValueError as ve:
        logger.error(f"ValueError in main: {ve}")
        st.error(f"ValueError in main: {ve}", icon="🚨")
    except TypeError as te:
        logger.error(f"TypeError in main: {te}")
        st.error(f"TypeError in main: {te}", icon="🚨")
    # We can add more specific exception handling as needed
    except Exception as e:
        logger.error(f"Error in main: {e}")
        st.error(f"Error in main: {e}", icon="🚨")
