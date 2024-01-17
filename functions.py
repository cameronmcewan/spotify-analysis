import streamlit as st
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import pandas as pd
import plotly.express as px

#########  Set up functions    ################################
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

@st.cache_data(ttl="59min")
def get_token(client_id, client_secret):
    try:
        auth_string = client_id + ":" + client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        result = post(url, headers=headers, data=data)
        result.raise_for_status()  # This will raise an error for HTTP error responses

        json_result = json.loads(result.content)
        token = json_result["access_token"]
        return token

    except Exception as e:
        st.error(f"Failed to get token: {e}")
        return None

# function to construct the header we need whenever we send another request
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

##############################################

############## Search Functions ##############
def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)

    # Check if 'artists' and 'items' keys exist
    if 'artists' in json_result and 'items' in json_result['artists']:
        if len(json_result['artists']['items']) == 0:
            st.write("No artist with this name exists...")
            return None
        return json_result['artists']['items'][0]
    else:
        st.error("Unexpected response format from Spotify API.")
        return None

def get_artist_suggestions(token, query_artist):
    if not query_artist: 
        return []
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    params = {
        'q': query_artist,
        'type': 'artist',
        'limit': 4
    }
    result = get(url=url, headers=headers, params=params)
    if result.status_code != 200:
        st.error("Error fetching artist data")
        return []
    json_result = result.json()["artists"]["items"]                                
    return json_result

def get_track_suggestions(token, query_track):
    if not query_track: 
        return []
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    params = {
        'q': query_track,
        'type': 'track',
        'limit': 5
    }
    result = get(url=url, headers=headers, params=params)
    if result.status_code != 200:
        st.error("Error fetching track data")
        return []
    json_result = result.json()["artists"]["items"]                                
    return json_result

def get_all_songs_by_artist(token, artist_id):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?type=track&q=artist:{artist_id}"
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]                                 
    if len(json_result) == 0:
        st.write("No artist with this name exists...")
        return None
    return json_result[0]

def search_for_track(token, track_name):
    try:
        url = "https://api.spotify.com/v1/search"
        headers = get_auth_header(token)
        params = {
            'q': track_name,
            'type': 'track',
            'limit': 5
        }
        result = get(url=url, headers=headers, params=params)
        json_result = result.json()
        
        track_suggestions = []
        track_mapping = {}

        if 'tracks' in json_result and 'items' in json_result['tracks']:
            for track in json_result['tracks']['items']:
                track_name = track['name']
                # Join the artist names into a single string
                artist_names = ', '.join(artist['name'] for artist in track['artists'])
                track_id = track['id']
                # Format each suggestion as "Track Name - Artist Name(s)"
                formatted_track = f"{track_name} - {artist_names}"
                track_suggestions.append(formatted_track)
                track_mapping[formatted_track] = track_id

        return track_suggestions, track_mapping

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return [], {}

##############################################

############### Artist functions #############

def get_top_tracks_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

##############################################

######### Audio Analysis functions ###########

def get_audio_analysis(token, song_id):
    url = f"https://api.spotify.com/v1/audio-analysis/{song_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def get_audio_features(token, song_id):
    url = f"https://api.spotify.com/v1/audio-features/{song_id}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def create_track_feature_radar_plot(token, song_id):
    # Fetch audio analysis and features
    audio_features = get_audio_features(token, song_id=song_id)

    # Extract required features
    song_danceability = audio_features["danceability"]
    song_acousticness = audio_features["acousticness"]
    song_energy = audio_features["energy"]
    song_instrumentalness = audio_features["instrumentalness"]
    song_liveness = audio_features["liveness"]
    song_speechiness = audio_features["speechiness"]
    song_valence = audio_features["valence"]

    # Create a DataFrame for the features
    df = pd.DataFrame({
        'r': [song_acousticness, song_danceability, song_energy, song_instrumentalness, song_liveness, song_speechiness, song_valence],
        'theta': ['Acousticness', 'Danceability', 'Energy', 'Instrumentalness', 'Liveness', 'Speechiness', 'Valence']
    })

    # Create the polar plot
    fig = px.line_polar(df, r='r', theta='theta', line_close=True, title="Track Audio Features")
    fig.update_traces(fill='toself')

    return fig