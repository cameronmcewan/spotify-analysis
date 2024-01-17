import streamlit as st
from dotenv import load_dotenv
import os
from functions import *
import plotly.express as px
import pandas as pd

########### Load environment variables ##############
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
token = get_token()


########### Initialize Streamlit app ################
def init_app():
    st.title("Spotify Analysis App")

    # Check for necessary tokens and credentials
    if token is None:
        st.error("Failed to retrieve the Spotify API Token.")
        st.stop()

    if client_id is None or client_secret is None:
        st.error("Client ID or Client Secret is not set.")
        st.stop()

############### SIDEBAR ####################
    
def artist_search_sidebar():
    query_artist = st.sidebar.text_input(label="Search for an artist")
    suggestions = get_artist_suggestions(token, query_artist)

    if suggestions:
        artist_names = [artist['name'] for artist in suggestions]
        selected_artist_name = st.sidebar.selectbox("Select an artist:", artist_names)
        if selected_artist_name:
            st.session_state['selected_artist'] = selected_artist_name
            st.write(f"Selected Artist: {selected_artist_name}")
    else:
        st.sidebar.write("No suggestions available")


################ MAIN PAGE ############################
def display_artist_info(query_artist):
    result = search_for_artist(token, query_artist)

    if result:
        artist_name = result["name"]
        artist_id = result["id"]
        artist_genres = result["genres"]
        artist_spotify_url = result["external_urls"]["spotify"]

        st.write("Your search found...", f"[{artist_spotify_url}]")
        st.header(artist_name)
        st.subheader("Associated Genres")
        for idx, genre in enumerate(artist_genres):
            st.write(f"{idx + 1}. {genre}")

        display_top_songs(artist_id)

#### Display top songs of the artist #######
def display_top_songs(artist_id):
    st.subheader("Top Songs")
    songs = get_top_tracks_by_artist(token, artist_id)
    for idx, song in enumerate(songs):
        st.write(f"{idx + 1}. {song['name']}")

########### Song analysis section ################
        
def song_analysis_section():
    st.subheader("Dive into a song analysis")
    track_name = st.text_input("Search for a track")
    track_suggestions, track_mapping = search_for_track(token, track_name)

    if track_suggestions:
        selected_track_name = st.selectbox("Select a track:", track_suggestions)
        if selected_track_name:
            selected_track_id = track_mapping[selected_track_name]
            st.session_state['selected_track'] = selected_track_name
            st.write(f"Selected Track: {selected_track_name}, ID: {selected_track_id}")
            display_song_features(selected_track_id)
    else:
        st.write("No track suggestions available.")

#### Display song features #####
def display_song_features(selected_track_id):
    st.subheader(f"Audio Features of {selected_track_id}")
    fig = create_track_feature_radar_plot(token, selected_track_id)
    st.plotly_chart(fig)


################################################################################################
################################################################################################
    
#####    Main App Execution  ###################
if __name__ == "__main__":
    init_app()
    artist_search_sidebar()
    if 'selected_artist' in st.session_state:
        display_artist_info(st.session_state['selected_artist'])
    song_analysis_section()