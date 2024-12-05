import os
from os.path import abspath
from flask import Blueprint, request, jsonify
from app.utils import extract_audio, transcribe_audio
from app.utils.scene_utils import describe_scene, ALL_CATEGORIES
from app.utils.video_utils import extract_keyframes

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
    transcription = data.get("transcription", "")  # Optional transcription
    output_dir = abspath("../keyframes")  # Convert keyframe directory to absolute path

    if not video_path or not os.path.exists(video_path):
        return jsonify({"error": "Video file not found"}), 400

    print(f"Received transcription: {transcription}")

    try:
        # Extract keyframes
        keyframes = extract_keyframes(video_path, output_dir)

        # Generate descriptions using categories
        descriptions = describe_scene(keyframes, ALL_CATEGORIES, transcription)

        # Convert all keyframe paths to absolute paths
        absolute_descriptions = {
            abspath(k): v for k, v in descriptions.items()
        }
        return jsonify({"keyframes": absolute_descriptions}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
from transformers import pipeline