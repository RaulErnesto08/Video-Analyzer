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

def extract_keyframes(video_path, output_dir):
    """
    Extract keyframes from a video using FFmpeg.
    :param video_path: Path to the input video file.
    :param output_dir: Directory to save the extracted keyframes.
    :return: List of extracted keyframe file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    keyframe_pattern = os.path.join(output_dir, "frame_%04d.jpeg")
    try:
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-vf", "select=eq(pict_type\\,I)", "-vsync", "vfr", keyframe_pattern],
            check=True
        )
        # Collect all keyframe file paths
        keyframes = [os.path.join(output_dir, f) for f in os.listdir(output_dir)]
        return sorted(keyframes)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg error: {str(e)}")
