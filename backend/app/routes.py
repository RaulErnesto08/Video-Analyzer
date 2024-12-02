import os
from flask import Blueprint, request, jsonify
from app.utils import extract_audio, transcribe_audio

main = Blueprint("main", __name__)

UPLOAD_FOLDER = "../input_videos"
AUDIO_FOLDER = "../audio_files"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)


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
    
    return jsonify({"message": "Video uploaded and audio extracted", "audio_path": audio_path}), 200

@main.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.get_json()
    audio_path = data.get("audio_path")
    
    if not audio_path or not os.path.exists(audio_path):
        return jsonify({"error" : "Audio file not found"}), 400
    
    try:
        transcription = transcribe_audio(audio_path)
        return jsonify({"transcription" : transcription})
    except Exception as e:
        return jsonify({"error" : str(e)}), 500