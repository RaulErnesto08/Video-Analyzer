import pytest
from unittest.mock import patch, MagicMock, mock_open
from app.utils.scene_utils import analyze_scenes_with_gpt_vision

@patch("app.utils.scene_utils.open", new_callable=mock_open, read_data=b"fake_image_data")
@patch("app.utils.scene_utils.OpenAI")
def test_analyze_scenes_with_gpt_vision(mock_openai, mock_open_file):
    # Mock OpenAI Client
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    # Mock API Response
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"frames": [{"frame_number": 1, "description": "Test Scene Description"}]}'
                )
            )
        ]
    )

    # Simulate Input Frames
    images = ["frame1.jpg", "frame2.jpg"]

    result = analyze_scenes_with_gpt_vision(images, api_key="test_api_key", language="English")

    assert len(result["frames"]) == 1
    assert result["frames"][0]["frame_number"] == 1
    assert result["frames"][0]["description"] == "Test Scene Description"
    
    mock_client.chat.completions.create.assert_called_once()
