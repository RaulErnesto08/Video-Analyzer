import pytest
from unittest.mock import patch, MagicMock
from app.utils.summarize_utils import generate_summary_with_gpt

@patch("app.utils.summarize_utils.OpenAI")
@patch("app.utils.summarize_utils.call_gpt_with_retries")
def test_generate_summary_with_gpt(mock_call_gpt_with_retries, mock_openai):
    # Mock OpenAI Client
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    # Mock API Response
    mock_call_gpt_with_retries.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"summary": "This is a test summary.", "tags": ["Tag1", "Tag2", "Tag3"]}'
                )
            )
        ]
    )

    # Simulated Input Data
    transcription = "This is a test transcription."
    scene_descriptions = {
        "frames": [
            {"frame_number": 1, "description": "Test frame 1 description."},
            {"frame_number": 2, "description": "Test frame 2 description."}
        ]
    }
    
    length = "concise"
    style = "formal"
    api_key = "test_api_key"
    language = "English"
    
    summary, tags = generate_summary_with_gpt(
        transcription=transcription,
        scene_descriptions=scene_descriptions,
        length=length,
        style=style,
        api_key=api_key,
        language=language
    )
    
    assert summary == "This is a test summary."
    assert tags == ["Tag1", "Tag2", "Tag3"]
    
    
    mock_call_gpt_with_retries.assert_called_once_with(
        mock_client,
        [
            {"role": "system", "content": "You are a helpful assistant for summarizing a video based on its transcription and scenes description."},
            {"role": "user", "content": (
                "Generate a structured summary and relevant topic tags for the video based on the input below:\n\n"
                "### Input Details:\n"
                "- Summary Length: concise\n"
                "- Summary Style: formal\n"
                "- Output Language: English\n"
                "### Transcription:\nThis is a test transcription.\n\n"
                "### Scene Descriptions:\nFrame 1: Test frame 1 description.\nFrame 2: Test frame 2 description.\n\n"
                "### Instructions:\n"
                "1. Create a concise summary of the video in a formal style.\n"
                "2. Extract and list up to 3 main topics discussed in the video as concise and specific topic tags.\n"
                "3. Ensure the summary and tags are written in English.\n\n"
                "### Output:\n"
            )}
        ],
        {
            "name": "summary_with_tags",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["summary", "tags"],
                "additionalProperties": False
            }
        }
    )
