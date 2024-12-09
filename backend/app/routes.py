import os
from os.path import abspath
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from app.utils import (
        extract_audio, extract_keyframes,
        transcribe_audio,
        analyze_scenes_with_gpt_vision,
        generate_summary_with_gpt,
    )

main = Blueprint("main", __name__)

UPLOAD_FOLDER = "../input_videos"
AUDIO_FOLDER = "../audio_files"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

load_dotenv()

@main.route("/")
def hello_world():
    return "Hello, Flask!"

@main.route("/upload", methods=["POST"])
def upload_video():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Extract audio from video
    audio_path = os.path.join(AUDIO_FOLDER, f"{os.path.splitext(file.filename)[0]}.wav")
    try:
        extract_audio(file_path, audio_path)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

    
    return jsonify({"message": "Video uploaded and audio extracted", "audio_path": audio_path, "file_path": file_path}), 200

@main.route("/transcribe_and_summarize", methods=["POST"])
def transcribe_and_summarize():
    data = request.get_json()
    audio_path = data.get("audio_path")
    length = data.get("length", "concise")
    style = data.get("style", "formal")

    if not audio_path or not os.path.exists(audio_path):
        return jsonify({"error": "Audio file not found"}), 400

    try:
        # Transcribe audio
        transcription = transcribe_audio(audio_path)

        # Generate summary
        summary = generate_summary_with_gpt(transcription, length, style, os.getenv("OPENAI_API_KEY"))

        return jsonify({"transcription": transcription, "summary": summary}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/scene_analysis", methods=["POST"])
def scene_analysis():
    data = request.get_json()
    video_path = data.get("video_path")
    output_dir = abspath("../keyframes")
    api_key = os.getenv("OPENAI_API_KEY")

    if not video_path or not os.path.exists(video_path):
        return jsonify({"error": "Video file not found"}), 400

    try:
        # Extract keyframes
        keyframes = extract_keyframes(video_path, output_dir)

        if not keyframes:
            return jsonify({"error": "No keyframes extracted from the video."}), 400

        scene_descriptions = analyze_scenes_with_gpt_vision(keyframes, api_key)

        return jsonify(scene_descriptions), 200
    except Exception as e:
        print(f"Error during scene analysis: {e}")
        return jsonify({"error": str(e)}), 500