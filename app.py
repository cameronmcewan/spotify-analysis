import streamlit as st
from dotenv import load_dotenv
import os
from functions import *

#####      Set page config       ###############
st.set_page_config(page_title="Spotify Analysis App", layout="wide")

########    Load environment variables ##############
load_dotenv()


########   Initialize Streamlit app ################
def init_app():
    token = get_token(client_id, client_secret)

    # Check for necessary tokens and credentials
    if token is None:
        st.error("Failed to retrieve the Spotify API Token.")
        st.stop()


    # Check for necessary tokens and credentials
    if token is None:
        st.error("Failed to retrieve the Spotify API Token.")
        st.stop()

    if client_id is None or client_secret is None:
        st.error("Client ID or Client Secret is not set.")
        st.stop()




if __name__ == "__main__":
    init_app()    