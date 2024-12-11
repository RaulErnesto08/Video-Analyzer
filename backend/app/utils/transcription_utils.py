import whisper

WHISPER_MODEL = whisper.load_model("base")

def transcribe_audio(audio_path, language=None):
    """
    Transcribe audio using Whisper.
    :param audio_path: Path to the audio file.
    :param language: Language override for transcription.
    :return: Transcription text and detected language.
    """
    try:
        result = WHISPER_MODEL.transcribe(audio_path, language=language)
        return {"text": result["text"], "language": result["language"]}
    except Exception as e:
        raise RuntimeError(f"Whisper transcription error: {str(e)}")
