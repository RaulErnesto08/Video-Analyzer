import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Video Analyzer", layout="wide")

st.title("Video Analyzer")

left_column, right_column = st.columns(2)

with left_column:
    st.header("Upload")

    uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov"])
    
    length_column, style_column = st.columns(2)
    with length_column:
        summary_length = st.selectbox("Summary Length", ["Concise", "Detailed"], key="length")
    with style_column:
        summary_style = st.selectbox("Summary Style", ["Formal", "Casual", "Technical"], key="style")
        
    if st.button("Generate Summary"):
        if uploaded_file is None:
            st.error("Please upload a video file first.")
        else:
            with st.spinner("Uploading and processing..."):
                files = {"file": ("video.mp4", uploaded_file.getvalue(), "video/mp4")}
                upload_response = requests.post(f"{BACKEND_URL}/upload", files=files)
            
            if upload_response.status_code == 200:
                st.success("Video uploaded and audio extracted successfully!")
                
                audio_path = upload_response.json().get("audio_path")
                
                with st.spinner("Generating summary..."):
                    summary_response = requests.post(
                        f"{BACKEND_URL}/transcribe_and_summarize",
                        json={
                            "audio_path": audio_path,
                            "length": summary_length.lower(),
                            "style": summary_style.lower(),
                        }
                    )
                
                if summary_response.status_code == 200:
                    result = summary_response.json()
                    st.session_state["transcription"] = result.get("transcription")
                    st.session_state["summary"] = result.get("summary")
                else:
                    st.error(f"Error: {summary_response.json().get('error')}")
            
            else:
                st.error(f"Error: {upload_response.json().get('error')}")
    
    if uploaded_file is not None:
        st.video(uploaded_file)
                
                
                

with right_column:
    st.header("Results")

    st.subheader("Transcript")
    if "transcription" in st.session_state:
        st.text_area("Transcription", st.session_state["transcription"], height=200)
    else:
        st.write("No transcription available.")

    st.subheader("Summary")
    if "summary" in st.session_state:
        st.text_area("Summary", st.session_state["summary"], height=200)
    else:
        st.write("No summary available.")