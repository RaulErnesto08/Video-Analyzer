import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:5000"

st.title("Video Analyzer")

uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov"])

if uploaded_file is not None:
    with st.spinner("Uploading and processing..."):
        files = {"file": ("video.mp4", uploaded_file.getvalue(), "video/mp4")}
        response = requests.post(f"{BACKEND_URL}/upload", files=files)

    if response.status_code == 200:
        st.success("Video uploaded and audio extracted successfully!")
        
        # Store the audio_path in session state
        audio_path = response.json().get("audio_path")
        st.session_state["audio_path"] = audio_path
        
        st.json(response.json())
    else:
        st.error(f"Error: {response.json().get('error')}")

# Call the transcription endpoint
if st.button("Transcribe Audio"):
    audio_path = st.session_state.get("audio_path")
    if not audio_path:
        st.error("Audio path not found. Upload a video first.")
    else:
        with st.spinner("Transcribing audio..."):
            response = requests.post(f"{BACKEND_URL}/transcribe", json={"audio_path": audio_path})
        
        if response.status_code == 200:
            st.success("Transcription completed!")
            transcription = response.json().get("transcription")
            st.text_area("Transcription", transcription, height=300)
        else:
            st.error(f"Error: {response.json().get('error')}")
