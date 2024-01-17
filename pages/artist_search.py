import streamlit as st
from functions import *

def artist_search_page(token):
    st.title("Artist Search")

    query_artist = st.text_input("Search for an artist")
    suggestions = get_artist_suggestions(token, query_artist)

    if suggestions:
        artist_names = [artist['name'] for artist in suggestions]
        selected_artist_name = st.selectbox("Select an artist:", artist_names)

        if selected_artist_name:
            result = search_for_artist(token, selected_artist_name)
            if result:
                st.write("Artist Details:")
                st.write(f"Name: {result['name']}")
                st.write(f"Genres: {', '.join(result['genres'])}")
                st.write(f"Spotify URL: {result['external_urls']['spotify']}")

if __name__ == "__main__":
    token = get_token(client_id, client_secret)
    artist_search_page(token)