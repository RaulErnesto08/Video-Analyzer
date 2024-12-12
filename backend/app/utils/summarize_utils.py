import json
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_gpt_with_retries(client, messages, json_schema):
    """
    Calls the GPT API with retries on failure.
    :param client: OpenAI API client instance.
    :param messages: Messages for GPT.
    :param json_schema: JSON schema for the response.
    :return: GPT response.
    """
    
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        response_format={"type": "json_schema", "json_schema": json_schema},
        max_tokens=1000,
        temperature=0.7,
    )

def generate_summary_with_gpt(transcription, scene_descriptions, length, style, api_key, language):
    """
    Generate a summary and video tags from transcription and scenes using GPT.
    :param transcription: The transcription text.
    :param scene_descriptions: The list of scene descriptions.
    :param length: Summary length (e.g., concise, detailed).
    :param style: Summary style (e.g., formal, casual, technical).
    :param api_key: OpenAI API key.
    :param language: The language of the transcription.
    :return: Generated summary text and video tags.
    """
    client = OpenAI(
        api_key=api_key
    )

    try:
        scene_text = "\n".join(
            [f"Frame {frame['frame_number']}: {frame['description']}" for frame in scene_descriptions["frames"]]
        )
        
        json_schema = {
            "name": "summary_with_tags",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["summary", "tags"],
                "additionalProperties": False
            }
        }
        
        prompt = (
            f"Generate a structured summary and relevant topic tags for the video based on the input below:\n\n"
            f"### Input Details:\n"
            f"- Summary Length: {length}\n"
            f"- Summary Style: {style}\n"
            f"- Output Language: {language}\n"
            f"### Transcription:\n"
            f"{transcription}\n\n"
            f"### Scene Descriptions:\n"
            f"{scene_text}\n\n"
            f"### Instructions:\n"
            f"1. Create a {length} summary of the video in a {style} style.\n"
            f"2. Extract and list up to 3 main topics discussed in the video as concise and specific topic tags.\n"
            f"3. Ensure the summary and tags are written in {language}.\n\n"
            f"### Output:\n"
        )

        messages = [
            {"role": "system", "content": "You are a helpful assistant for summarizing a video based on its transcription and scenes description."},
            {"role": "user", "content": prompt}
        ]
        
        response = call_gpt_with_retries(client, messages, json_schema)
        result = json.loads(response.choices[0].message.content)

        result = json.loads(response.choices[0].message.content)
        return result["summary"], result["tags"]
    except Exception as e:
        print(f"Error generating summary with GPT: {e}")
        return None, []
