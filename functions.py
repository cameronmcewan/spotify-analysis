import streamlit as st
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

load_dotenv()

client_id = os.getenv("CLIENT_ID")
# client_id = '4258700cad6348589634464fd9083443'
client_secret = os.getenv("CLIENT_SECRET")
# client_secret = '5edd7d5821ff49a1ab236d8014ef36bc'

if client_id is None or client_secret is None:
    st.error("Client ID or Client Secret is not set.")
    st.stop()

@st.cache_data(ttl="59min")
def get_token():
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
        return json_result["access_token"]

    except Exception as e:
        st.error(f"Failed to get token: {e}")
        return None

# function to construct the header we need whenever we send another request
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

# https://api.spotify.com/v1/audio-analysis/{id}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
                                             
    if len(json_result) == 0:
        st.write("No artist with this name exists...")
        return None

    return json_result[0]

def get_top_tracks_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
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