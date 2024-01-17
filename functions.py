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

##############################################
# Set up functions 
# ~~~~~~~~~~~~~~~~
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

##############################################

############## Search Functions ##############

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

# def search_for_track(token, track_name):
#     url = "https://api.spotify.com/v1/search"
#     headers = get_auth_header(token)
#     # query = f"?type=track&q={track_name}&limit=1"
#     params = {
#         'q': track_name,
#         'type': 'track',
#         'limit': 5
#     }
#     result = get(url=url, headers=headers, params=params)
#     json_result = result.json()
#     # if json_result['tracks']['items']:
#     #     track_id = json_result['tracks']['items']['id']
#     #     return track_id
#     # else:
#     #     return None

#     # Dropdown for artist selection
#     suggestions = json_result['tracks']['items']
#     if suggestions:
#         track_suggestions = [track['name'] for track in suggestions]
#         selected_track_name = st.selectbox("Select a track:", track_suggestions)
#         if selected_track_name:
#             st.session_state['selected_track'] = selected_track_name
#             st.write(f"Selected Track: {selected_track_name}")
#     else:
#         st.sidebar.write("No suggestions available")

#     return json_result['tracks']['items'][name=selected_track_name]

# def search_for_track(token, track_name):
#     url = "https://api.spotify.com/v1/search"
#     headers = get_auth_header(token)
#     params = {
#         'q': track_name,
#         'type': 'track',
#         'limit': 5
#     }
#     result = get(url=url, headers=headers, params=params)
#     json_result = result.json()
    
#     track_suggestions = []
#     track_mapping = {}

#     if 'tracks' in json_result and 'items' in json_result['tracks']:
#         for track in json_result['tracks']['items']:
#             track_name = track['name']
#             track_artists = track['artists']
#             track_id = track['id']
#             track_suggestions.append([track_name, track_artists])
#             track_mapping[track_name] = track_id

#     return track_suggestions, track_mapping

def search_for_track(token, track_name):
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