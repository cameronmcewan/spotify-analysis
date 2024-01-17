import streamlit as st
from functions import *

def song_analysis_page(token):
    st.title("Song Analysis")

    track_name = st.text_input("Search for a track")
        
    if track_name:
        st.write(f"Debug: track_name = {track_name}, type = {type(track_name)}")
        track_suggestions, track_mapping = search_for_track(token, track_name)

        if track_suggestions:
            selected_track_name = st.selectbox("Select a track:", track_suggestions)

            if selected_track_name:
                selected_track_id = track_mapping[selected_track_name]
                st.write(f"Selected Track: {selected_track_name}, ID: {selected_track_id}")

                fig = create_track_feature_radar_plot(token, selected_track_id)
                st.plotly_chart(fig)
    else:
        st.write("Please enter a track name to search.")




if __name__ == "__main__":
    token = get_token(client_id, client_secret)
    song_analysis_page(token)