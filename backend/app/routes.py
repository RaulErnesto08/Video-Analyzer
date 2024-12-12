import os
import uuid
import asyncio
from os.path import abspath
from datetime import datetime
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from app.utils import (
        extract_audio, extract_keyframes,
        transcribe_audio,
        analyze_scenes_with_gpt_vision,
        generate_summary_with_gpt,
    )

main = Blueprint("main", __name__)

UPLOAD_BASE_DIR = "../uploads"

load_dotenv()

@main.route("/upload", methods=["POST"])
def upload_video():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    # Generate a unique subdirectory for this upload
    unique_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    video_dir = os.path.join(UPLOAD_BASE_DIR, unique_id)
    os.makedirs(video_dir, exist_ok=True)

    # Save uploaded video
    video_filename = f"{unique_id}_{file.filename}"
    video_path = os.path.join(video_dir, video_filename)
    file.save(video_path)

    # Extract audio
    audio_dir = os.path.join(video_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    audio_path = os.path.join(audio_dir, f"{unique_id}_audio.wav")

    try:
        extract_audio(video_path, audio_path)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

    # Extract keyframes directly into the `keyframes` folder in the video's directory
    keyframes_dir = os.path.join(video_dir, "keyframes")
    try:
        keyframes = extract_keyframes(video_path, keyframes_dir)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Video uploaded, audio extracted, and keyframes generated",
        "video_path": video_path,
        "audio_path": audio_path,
        "keyframes": keyframes
    }), 200

@main.route("/generate_summary", methods=["POST"])
async def generate_summary():
    data = request.get_json()
    audio_path = data.get("audio_path")
    video_path = data.get("video_path")
    length = data.get("length", "concise")
    style = data.get("style", "formal")
    language = data.get("language")
    api_key = os.getenv("OPENAI_API_KEY")
    
    video_dir = os.path.dirname(video_path)
    keyframes_dir = os.path.join(video_dir, "keyframes")

    if not audio_path or not os.path.exists(audio_path):
        return jsonify({"error": "Audio file not found"}), 400
    if not video_path or not os.path.exists(video_path):
        return jsonify({"error": "Video file not found"}), 400

    try:
        # Asynchronously run transcription and scene processing
        async def run_tasks():
            transcription_task = asyncio.create_task(asyncio.to_thread(transcribe_audio, audio_path, language))
            
            keyframes = await asyncio.to_thread(extract_keyframes, video_path, keyframes_dir)

            if not keyframes:
                raise RuntimeError("No keyframes extracted, cannot proceed with scene analysis.")

            # Run scene analysis after keyframes are extracted
            scene_descriptions = await asyncio.to_thread(analyze_scenes_with_gpt_vision, keyframes, api_key, language)
            transcription = await transcription_task

            return transcription, scene_descriptions

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
