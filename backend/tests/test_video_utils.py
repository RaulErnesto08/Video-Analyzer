import pytest
from app.utils.video_utils import extract_audio, extract_keyframes
from unittest.mock import patch, MagicMock

@patch("subprocess.run")
def test_extract_audio(mock_run):
    # Mock FFmpeg Call
    mock_run.return_value = MagicMock()
    
    # Test Audio Extraction
    result = extract_audio("path/to/video.mp4", "output/audio.wav")
    assert result == "output/audio.wav"
    mock_run.assert_called_once_with(
        ["ffmpeg", "-i", "path/to/video.mp4", "-q:a", "0", "-map", "a", "output/audio.wav"],
        check=True
    )

@patch("subprocess.run")
@patch("os.listdir")
def test_extract_keyframes(mock_listdir, mock_run):
    # Mock FFmpeg and Filesystem Calls
    mock_run.return_value = MagicMock()
    mock_listdir.return_value = ["frame_0001.jpeg", "frame_0002.jpeg"]

    result = extract_keyframes("path/to/video.mp4", "output/keyframes")
    assert result == ["output/keyframes/frame_0001.jpeg", "output/keyframes/frame_0002.jpeg"]
    mock_run.assert_called_once()
