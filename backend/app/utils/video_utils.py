import os
import math
import subprocess

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

def extract_keyframes(video_path, output_dir, num_frames=10):
    """
    Extract keyframes from a video using FFmpeg.
    :param video_path: Path to the input video file.
    :param output_dir: Directory to save the extracted keyframes.
    :param num_frames: Maximum number of keyframes to extract.
    :return: List of extracted keyframe file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    unique_id = os.path.basename(video_path).split("_")[0]
    keyframe_pattern = os.path.join(output_dir, f"{unique_id}_frame_%04d.jpeg")
    
    try:
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-vf", "select=eq(pict_type\\,I)", "-vsync", "vfr", keyframe_pattern],
            check=True
        )
        
        # Collect all keyframe file paths
        keyframes = sorted([os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(".jpeg")])
        
        # Uniformly sample the keyframes
        total_frames = len(keyframes)
        if total_frames <= num_frames:
            return keyframes
        else:
            # Calculate indices for uniform sampling
            step = total_frames / num_frames
            sampled_indices = [math.floor(i * step) for i in range(num_frames)]
            sampled_keyframes = [keyframes[i] for i in sampled_indices]
            return sampled_keyframes
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg error: {str(e)}")
