import subprocess
import os

def extract_audio(video_path, output_path):
    """
    Extract audio from a video file using FFmpeg.
    :param video_path: Path to the input video file.
    :param output_path: Path to save the extracted audio.
    :return: Path to the extracted audio file.
    """
    try:
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", output_path],
            check=True
        )
        return output_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg error: {str(e)}")
