import torch
import clip
from PIL import Image
from transformers import pipeline

# COCO Categories
COCO_CATEGORIES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "TV", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear",
    "hair drier", "toothbrush"
]

# Custom Categories for Educational Content
CUSTOM_CATEGORIES = [
    "photosynthesis", "chloroplast", "plant cell", "glucose", "light energy",
    "carbon dioxide", "oxygen", "thylakoid", "stroma", "Calvin cycle",
    "leaves", "roots", "sunlight", "plant", "tree", "ecosystem", "biology"
]

# Merged Categories
ALL_CATEGORIES = list(set(COCO_CATEGORIES + CUSTOM_CATEGORIES))

def split_transcription(transcription, max_length=512):
    """
    Split transcription into smaller chunks within the max token limit.
    """
    words = transcription.split()
    for i in range(0, len(words), max_length):
        yield " ".join(words[i:i + max_length])

def extract_keywords_with_transformers(transcription):
    """
    Extract keywords from large transcriptions by splitting into smaller chunks.
    """
    ner_pipeline = pipeline("ner", model="allenai/scibert_scivocab_uncased", grouped_entities=True)
    keywords = []

    for chunk in split_transcription(transcription):
        entities = ner_pipeline(chunk)
        keywords.extend([entity["word"] for entity in entities if entity["score"] > 0.7])

    # Remove duplicates
    return list(set(keywords))

def refine_labels_with_transcription(transcription, default_labels):
    """
    Refine default labels using keywords extracted with Transformers.
    :param transcription: Transcription text.
    :param default_labels: Predefined labels for scene analysis.
    :return: Refined label list.
    """
    keywords = extract_keywords_with_transformers(transcription)
    refined_labels = default_labels + [f"a scene with {keyword}" for keyword in keywords]
    return refined_labels

def generate_prompts_from_categories(categories):
    """
    Generate descriptive prompts for scene analysis.
    :param categories: List of categories.
    :return: List of descriptive prompts.
    """
    return [f"This is an image of a {category}." for category in categories]


def describe_scene(keyframes, all_categories, transcription=None):
    """
    Generate descriptions for video keyframes using CLIP.
    :param keyframes: List of keyframe image paths.
    :param all_categories: categories for scene analysis.
    :param transcription: (Optional) Transcription text for refining labels.
    :return: List of descriptions for each keyframe.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    # Generate and refine prompts
    default_labels = generate_prompts_from_categories(all_categories)
    if transcription:
        default_labels = refine_labels_with_transcription(transcription, default_labels)

    # Tokenize prompts
    text_inputs = torch.cat([clip.tokenize(label) for label in default_labels]).to(device)

    descriptions = {}
    for keyframe in keyframes:
        try:
            image = preprocess(Image.open(keyframe)).unsqueeze(0).to(device)
            with torch.no_grad():
                image_features = model.encode_image(image)
                text_features = model.encode_text(text_inputs)
                similarity = (image_features @ text_features.T).softmax(dim=-1)
                top_match = similarity.argmax().item()

            descriptions[keyframe] = {
                "description": default_labels[top_match],
                "confidence": similarity[0, top_match].item()
            }
        except Exception as e:
            descriptions[keyframe] = {"error": str(e)}

    return descriptions
