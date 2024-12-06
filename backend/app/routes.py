import os
from os.path import abspath
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from app.utils import (
        extract_audio, extract_keyframes,
        transcribe_audio, 
        extract_keywords_with_gpt, describe_scene,
        generate_summary_with_gpt
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

    # Debugging
    print(f"Video Path: {file_path}")
    print(f"Audio Path: {audio_path}")
    
    return jsonify({"message": "Video uploaded and audio extracted", "audio_path": audio_path, "file_path": file_path}), 200

@main.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json()
    audio_path = data.get("audio_path")
    
    if not audio_path or not os.path.exists(audio_path):
        print(f"Audio Path Not Found: {audio_path}")
        return jsonify({"error" : "Audio file not found"}), 400
    
    try:
        transcription = transcribe_audio(audio_path)
        return jsonify({"transcription" : transcription})
    except Exception as e:
        return jsonify({"error" : str(e)}), 500

@main.route("/scene_analysis", methods=["POST"])
def scene_analysis():
    data = request.get_json()
    video_path = data.get("video_path")
    transcription = data.get("transcription", "")
    output_dir = abspath("../keyframes")
    api_key = os.getenv("OPENAI_API_KEY")

    if not video_path or not os.path.exists(video_path):
        return jsonify({"error": "Video file not found"}), 400

    try:
        # Extract keyframes
        keyframes = extract_keyframes(video_path, output_dir)

        # Generate keywords with GPT
        if transcription:
            keywords = extract_keywords_with_gpt(transcription, api_key)
            if not keywords:
                return jsonify({"error": "Failed to extract keywords with GPT"}), 500
        else:
            keywords = []

        # Generate descriptions using keywords
        descriptions = describe_scene(keyframes, keywords, transcription)
        return jsonify({"keyframes": descriptions}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    transcription = data.get("transcription", "")
    length = data.get("length", "concise")
    style = data.get("style", "formal")
    api_key = os.getenv("OPENAI_API_KEY")

    if not transcription:
        return jsonify({"error": "Transcription not provided"}), 400

    try:
        summary = generate_summary_with_gpt(transcription, length, style, api_key)
        if not summary:
            return jsonify({"error": "Failed to generate summary"}), 500

        return jsonify({"summary": summary}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
