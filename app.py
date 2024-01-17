import streamlit as st
from dotenv import load_dotenv
import os
from functions import *
import plotly.express as px
import pandas as pd

load_dotenv()
token = get_token()

st.title("Spotify Analysis App")
if token is None:
    st.error("Failed to retrieve the Spotify API Token.")
    st.stop()

if client_id is None or client_secret is None:
    st.error("Client ID or Client Secret is not set.")
    st.stop()


artist_name = st.sidebar.text_input(label="Search for an artist") 
result = search_for_artist(token, artist_name)
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

st.subheader("Audio Features")
st.write("Example audio analysis response:")
 
example_song_id = "11dFghVXANMlKmJXsNCbNl"
song_analysis = get_audio_analysis(token, song_id=example_song_id)
song_tempo = get_audio_analysis(token, song_id=example_song_id)["track"]["tempo"]
st.write(song_analysis)
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