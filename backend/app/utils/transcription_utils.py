import whisper

def transcribe_audio(audio_path, language=None):
    """
    Transcribe audio using Whisper.
    :param audio_path: Path to the audio file.
    :param language: Language override for transcription.
    :return: Transcription text and detected language.
    """
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, language=language)
    return {"text": result["text"], "language": result["language"]}
