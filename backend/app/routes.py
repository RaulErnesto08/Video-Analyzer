from flask import Blueprint, request, jsonify
import os
import subprocess
import whisper

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
        subprocess.run(
            ["ffmpeg", "-i", file_path, "-q:a", "0", "-map", "a", audio_path],
            check=True
        )
    except subprocess.CalledProcessError:
        return jsonify({"error": "Error extracting audio"}), 500
    
    return jsonify({"message": "Video uploaded and audio extracted", "audio_path": audio_path}), 200

@main.route("/transcribe", methods=["POST"])
def transcribe_audio():
    data = request.get_json()
    audio_path = data.get("audio_path")
    
    if not audio_path or not os.path.exists(audio_path):
        return jsonify({"error" : "Audio file not found"}), 400
    
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return jsonify({"transcription" : result["text"]})
    except Exception as e:
        return jsonify({"error" : str(e)}), 500