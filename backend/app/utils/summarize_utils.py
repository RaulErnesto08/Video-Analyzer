from openai import OpenAI

def generate_summary_with_gpt(transcription, length, style, api_key):
    """
    Generate a summary from transcription using GPT.
    :param transcription: The transcription text.
    :param length: Summary length (e.g., concise, detailed).
    :param style: Summary style (e.g., formal, casual, technical).
    :param api_key: OpenAI API key.
    :return: Generated summary text.
    """
    client = OpenAI(
        api_key=api_key
    )

    try:
        prompt = (
            f"Summarize the following transcription in a {length} and {style} style:\n\n"
            f"Transcription:\n{transcription}\n\nSummary:"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for summarizing text."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.5
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating summary with GPT: {e}")
        return None
