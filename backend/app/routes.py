import os
import asyncio

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

@main.route("/generate_summary", methods=["POST"])
async def generate_summary():
    data = request.get_json()
    audio_path = data.get("audio_path")
    video_path = data.get("video_path")
    length = data.get("length", "concise")
    style = data.get("style", "formal")
    language = data.get("language")
    output_dir = abspath("../keyframes")
    api_key = os.getenv("OPENAI_API_KEY")

    if not audio_path or not os.path.exists(audio_path):
        return jsonify({"error": "Audio file not found"}), 400
    if not video_path or not os.path.exists(video_path):
        return jsonify({"error": "Video file not found"}), 400

    try:
        # Asynchronously run transcription and scene processing
        async def run_tasks():
            # Run transcription and keyframe extraction in parallel
            transcription = asyncio.create_task(asyncio.to_thread(transcribe_audio, audio_path, language))
            keyframes = await asyncio.to_thread(extract_keyframes, video_path, output_dir)
            scene_descriptions = await asyncio.to_thread(analyze_scenes_with_gpt_vision, keyframes, api_key, language)

            return await transcription, scene_descriptions

        transcription, scene_descriptions = await run_tasks()

        summary, tags = generate_summary_with_gpt(
            transcription=transcription["text"],
            language=transcription["language"],
            scene_descriptions=scene_descriptions,
            length=length,
            style=style,
            api_key=api_key,
        )

        return jsonify({
            "transcription": transcription["text"],
            "language": transcription["language"],
            "scene_descriptions": scene_descriptions,
            "summary": summary,
            "tags": tags,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
