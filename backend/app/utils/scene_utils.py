import json
import torch
import clip
from PIL import Image
from openai import OpenAI

def extract_keywords_with_gpt(transcription, api_key):
    """
    Extract keywords from transcription using GPT.
    :param transcription: The transcription text.
    :param api_key: Your OpenAI API key.
    :return: List of keywords.
    """
    client = OpenAI(
        api_key=api_key
    )
    
    json_schema = {
        "name": "keyword_extraction",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "A list of relevant keywords extracted from the transcription."
                }
            },
            "required": ["keywords"],
            "additionalProperties": False
        }
    }

    try:
        prompt = (
            "Extract the most important and relevant keywords from the following transcription. "
            "Ensure the keywords are concise, unique, and meaningful:\n\n"
            f"Transcription:\n{transcription}\n\nKeywords:"
        )

        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for text analysis."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_schema", "json_schema": json_schema},
            max_tokens=150,
            temperature=0.5
        )

        print(response)
        
        response_content = response.choices[0].message.content
        keywords_data = json.loads(response_content)
        return keywords_data.get("keywords")
    
    except Exception as e:
        print(f"Error using GPT for keyword extraction: {e}")
        return None

def generate_prompts_from_categories(categories):
    """
    Generate descriptive prompts for scene analysis.
    :param categories: List of categories.
    :return: List of descriptive prompts.
    """
    return [f"This is an image of a {category}." for category in categories]

def describe_scene(keyframes, keywords, transcription=None, batch_size=50):
    """
    Generate descriptions for video keyframes using CLIP with batched prompts.
    :param keyframes: List of keyframe image paths.
    :param keywords: Keywords for scene analysis.
    :param transcription: (Optional) Transcription text for refining labels.
    :param batch_size: Maximum number of prompts to process in a single batch.
    :return: List of descriptions for each keyframe.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-L/14", device=device)

    # Generate and refine prompts
    prompts = generate_prompts_from_categories(keywords)

    # Split prompts into batches
    batched_prompts = [prompts[i:i + batch_size] for i in range(0, len(prompts), batch_size)]

    descriptions = {}
    for keyframe in keyframes:
        try:
            image = preprocess(Image.open(keyframe)).unsqueeze(0).to(device)
            print(f"Processing keyframe: {keyframe} - Image tensor size: {image.size()}")

            highest_confidence = 0
            best_description = "No matching description"

            # Process each batch of prompts
            for batch in batched_prompts:
                text_inputs = torch.cat([clip.tokenize(label) for label in batch]).to(device)
                print(f"Processing batch of size {len(batch)} - Text tensor size: {text_inputs.size()}")

                with torch.no_grad():
                    image_features = model.encode_image(image)
                    text_features = model.encode_text(text_inputs)
                    print(f"Image features: {image_features.size()}, Text features: {text_features.size()}")

                    similarity = (image_features @ text_features.T).softmax(dim=-1)

                # Find the best match in the current batch
                top_match = similarity.argmax().item()
                confidence = similarity[0, top_match].item()

                if confidence > highest_confidence:
                    highest_confidence = confidence
                    best_description = batch[top_match]

            descriptions[keyframe] = {
                "description": best_description,
                "confidence": highest_confidence
            }
        except Exception as e:
            descriptions[keyframe] = {"error": str(e)}

    return descriptions
