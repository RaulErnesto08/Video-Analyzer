from openai import OpenAI

def generate_summary_with_gpt(transcription, scene_descriptions, length, style, api_key):
    """
    Generate a summary from transcription using GPT.
    :param transcription: The transcription text.
    :param scene_descriptions: The list of scene descriptions.
    :param length: Summary length (e.g., concise, detailed).
    :param style: Summary style (e.g., formal, casual, technical).
    :param api_key: OpenAI API key.
    :return: Generated summary text.
    """
    client = OpenAI(
        api_key=api_key
    )

    try:
        scene_text = "\n".join(
            [f"Frame {frame['frame_number']}: {frame['description']}" for frame in scene_descriptions["frames"]]
        )
        
        prompt = (
            f"Create a {length} and {style} summary based on the following:\n\n"
            f"Transcription:\n{transcription}\n\n"
            f"Scene Descriptions:\n{scene_text}\n\n"
            "Summary:"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for summarizing a video based on its transcription and scenes description."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating summary with GPT: {e}")
        return None
