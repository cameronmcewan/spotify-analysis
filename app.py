import streamlit as st
from dotenv import load_dotenv
import os
from functions import *
import plotly.express as px
import pandas as pd

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
token = get_token()

st.title("Spotify Analysis App")

if token is None:
    st.error("Failed to retrieve the Spotify API Token.")
    st.stop()

if client_id is None or client_secret is None:
    st.error("Client ID or Client Secret is not set.")
    st.stop()

############### SIDEBAR ####################
    
query_artist = st.sidebar.text_input(label="Search for an artist") 
# Get suggestions (API call simulation)
suggestions = get_artist_suggestions(token, query_artist)

# Dropdown for artist selection
if suggestions:
    artist_names = [artist['name'] for artist in suggestions]
    selected_artist_name = st.sidebar.selectbox("Select an artist:", artist_names)
    if selected_artist_name:
        st.session_state['selected_artist'] = selected_artist_name
        st.write(f"Selected Artist: {selected_artist_name}")
else:
    st.sidebar.write("No suggestions available")

############################################


result = search_for_artist(token, query_artist)

artist_name = result["name"]
artist_id = result["id"]
artist_genres = result["genres"]
artist_spotify_url = result["external_urls"]["spotify"]

st.write("Your search found...", f"[{artist_spotify_url}]")
st.header(artist_name)

st.subheader("Associated Genres")
for idx, genre in enumerate(artist_genres):
    st.write(f"{idx + 1}. { genre}")

st.subheader("Top Songs")
songs = get_top_tracks_by_artist(token, artist_id)
for idx, song in enumerate(songs):
    st.write(f"{idx + 1}. { song['name']}")

st.subheader("Dive into a song analysis")

#########################################################

track_name = st.text_input("Search for a track")
track_suggestions, track_mapping = search_for_track(token, track_name)

if track_suggestions:
    selected_track_name = st.selectbox("Select a track:", track_suggestions)
    if selected_track_name:
        selected_track_id = track_mapping[selected_track_name]
        st.session_state['selected_track'] = selected_track_name
        st.write(f"Selected Track: {selected_track_name}, ID: {selected_track_id}")
else:
    st.write("No track suggestions available.")


#########################################################

st.subheader(f"Audio Features of {track_name}")
# st.write("Example audio analysis response:")
example_song_id = "11dFghVXANMlKmJXsNCbNl"
# song_analysis = get_audio_analysis(token, song_id=example_song_id)

song_tempo = get_audio_analysis(token, song_id=example_song_id)["track"]["tempo"]
# st.write(song_analysis)
song_danceability = get_audio_features(token, song_id=example_song_id)["danceability"]
song_acousticness = get_audio_features(token, song_id=example_song_id)["acousticness"]
song_energy = get_audio_features(token, song_id=example_song_id)["energy"]
song_instrumentalness = get_audio_features(token, song_id=example_song_id)["instrumentalness"]
song_liveness = get_audio_features(token, song_id=example_song_id)["liveness"]
song_speechiness = get_audio_features(token, song_id=example_song_id)["speechiness"]
song_valence = get_audio_features(token, song_id=example_song_id)["valence"]

df = pd.DataFrame(dict(
    r=[song_acousticness, song_danceability, song_energy, song_liveness, song_speechiness, song_valence],
    theta=['Acousticness', 'Danceability', 'Energy', 'Liveness', 'Speechiness', 'Valence']))
fig = px.line_polar(df, r='r', theta='theta', line_close=True, title="Song Features")
fig.update_traces(fill='toself')

st.plotly_chart(fig)