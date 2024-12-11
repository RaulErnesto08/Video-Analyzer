import base64
import json
from openai import OpenAI

def analyze_scenes_with_gpt_vision(images, api_key, language="English"):
    """
    Analyze scenes using GPT-4 Vision in a single batch request.
    :param images: List of file paths for the keyframe images.
    :param api_key: OpenAI API key.
    :param language: Language for scene descriptions.
    :return: Descriptions of the scenes.
    """
    client = OpenAI(api_key=api_key)

    base64_frames = []
    for image_path in images:
        with open(image_path, "rb") as image_file:
            base64_frame = base64.b64encode(image_file.read()).decode("utf-8")
            base64_frames.append(base64_frame)

    json_schema = {
        "name": "scene_analysis",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "frames": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "frame_number": {"type": "integer"},
                            "description": {"type": "string"},
                        },
                        "required": ["frame_number", "description"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["frames"],
            "additionalProperties": False
        }
    }

    prompt = [
        f"These are frames from a video. Analyze each frame and provide a detailed description of the scene in {language}.",
        *map(lambda x: {"image": x, "resize": 1024}, base64_frames),
    ]

    PROMPT_MESSAGES = [
        {"role": "system", "content": "You are a scene analyzer who provides detailed descriptions for video frames."},
        {"role": "user", "content": prompt},
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=PROMPT_MESSAGES,
            response_format={"type": "json_schema", "json_schema": json_schema},
            max_tokens=1000,
            temperature=0.5,
        )

        # Parse and return the structured JSON response
        structured_response = json.loads(response.choices[0].message.content)
        
        for i, frame in enumerate(structured_response["frames"]):
            frame["frame_path"] = images[i]

        return structured_response
    except Exception as e:
        print(f"Error analyzing scenes with GPT Vision: {e}")
        return {"error": str(e)}