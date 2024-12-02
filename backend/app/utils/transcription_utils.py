import whisper

def transcribe_audio(audio_path):
    """
    Transcribe audio using Whisper.
    :param audio_path: Path to the audio file.
    :return: Transcription text.
    """
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]
