import json
import requests
import streamlit as st
from streamlit_tags import st_tags

BACKEND_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Video Analyzer", layout="wide")

st.title("Video Analyzer")

# Helper function to reset session state
def reset_session_state():
    st.session_state["transcription"] = None
    st.session_state["scene_descriptions"] = []
    st.session_state["summary"] = None
    st.session_state["tags"] = []
    st.session_state["uploaded_file_id"] = None

left_column, right_column = st.columns(2)

with left_column:
    st.header("Upload")

    uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov"])
    
    language = st.selectbox(
        "Language",
        options=["Video's default", "English", "Spanish", "French", "German", "Chinese", "Japanese"],
        key="language"
    )
    
    length_column, style_column = st.columns(2)
    with length_column:
        summary_length = st.selectbox("Summary Length", ["Concise", "Detailed"], key="length")
    with style_column:
        summary_style = st.selectbox("Summary Style", ["Formal", "Casual", "Technical"], key="style")
        
    if st.button("Generate Summary"):
        if uploaded_file is None:
            st.error("Please upload a video file first.")
        else:
            reset_session_state()

            # Set a unique ID for the uploaded file
            st.session_state["uploaded_file_id"] = uploaded_file.name + str(uploaded_file.size)

            with st.spinner("Uploading and processing..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                upload_response = requests.post(f"{BACKEND_URL}/upload", files=files)
            
            if upload_response.status_code == 200:
                st.success("Video uploaded and audio extracted successfully!")
                
                audio_path = upload_response.json().get("audio_path")
                video_path = upload_response.json().get("video_path")
                
                with st.spinner("Generating summary..."):
                    summary_response = requests.post(
                        f"{BACKEND_URL}/generate_summary",
                        json={
                            "audio_path": audio_path,
                            "video_path": video_path,
                            "length": summary_length.lower(),
                            "style": summary_style.lower(),
                            "language": None if language == "Video's default" else language.lower(),
                        }
                    )
                
                if summary_response.status_code == 200:
                    result = summary_response.json()
                    st.session_state["transcription"] = result.get("transcription")
                    st.session_state["scene_descriptions"] = result.get("scene_descriptions", {}).get("frames", [])
                    st.session_state["summary"] = result.get("summary")
                    st.session_state["tags"] = result.get("tags")
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
        st.download_button(
            label="Download Summary",
            data=st.session_state["summary"],
            file_name="summary.txt",
            mime="text/plain"
        )
    else:
        st.write("No summary available.")
    
    if "tags" in st.session_state and st.session_state["tags"]:
        st_tags(
            label="Video Tags:",
            text="",
            value=st.session_state["tags"],
            suggestions=[],
            key=f"tags_display_{st.session_state.get('uploaded_file_id', 'default')}"
        )
    
    if "scene_descriptions" in st.session_state:
        st.subheader("Scene Descriptions")
        with st.expander("View Scene Descriptions"):
            for frame in st.session_state["scene_descriptions"]:
                st.image(frame.get("frame_path"), caption=f"Frame {frame.get('frame_number')}")
                st.write(frame.get("description"))
                
    if "transcription" in st.session_state:
        scene_descriptions_without_paths = [
            {"description": frame.get("description"), "frame_number": frame.get("frame_number")}
            for frame in st.session_state.get("scene_descriptions", [])
        ]
        
        results = {
            "transcription": st.session_state.get("transcription"),
            "summary": st.session_state.get("summary"),
            "tags": st.session_state.get("tags"),
            "scene_descriptions": scene_descriptions_without_paths
        }
        
        results_json = json.dumps(results, indent=4)
        st.download_button(
            label="Download All Results",
            data=results_json,
            file_name="results.json",
            mime="application/json"
        )
    else:
        st.write("No results to download.")