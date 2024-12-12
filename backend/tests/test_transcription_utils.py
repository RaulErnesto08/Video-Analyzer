import pytest
from app.utils.transcription_utils import transcribe_audio
from unittest.mock import patch

# Mock Whisper Model
@patch("app.utils.transcription_utils.WHISPER_MODEL.transcribe")
def test_transcribe_audio(mock_transcribe):
    # Mock Response
    mock_transcribe.return_value = {"text": "Hello World", "language": "English"}
    
    result = transcribe_audio("path/to/audio/file.wav")
    assert result["text"] == "Hello World"
    assert result["language"] == "English"

@patch("app.utils.transcription_utils.WHISPER_MODEL.transcribe")
def test_transcribe_audio_with_language(mock_transcribe):
    mock_transcribe.return_value = {"text": "Hola Mundo", "language": "Spanish"}
    
    result = transcribe_audio("path/to/audio/file.wav", language="Spanish")
    assert result["text"] == "Hola Mundo"
    assert result["language"] == "Spanish"
