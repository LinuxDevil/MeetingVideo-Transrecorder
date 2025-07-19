"""
Transcription module using Whisper
"""

import whisper
from typing import Optional
from src.config import config
from src.utils import setup_logging
import os

logger = setup_logging(level=config.log_level)

class Transcriber:
    """Whisper transcription handler"""
    def __init__(self):
        self.model = whisper.load_model(config.whisper.model_size)

    def transcribe(self, audio_file: str) -> Optional[str]:
        """Transcribe audio to text using Whisper"""
        logger.info(f"Transcribing audio file: {audio_file}")
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return None

        try:
            result = self.model.transcribe(audio_file, task=config.whisper.task, language=config.whisper.language)
            transcript = result.get('text', '')

            transcript_file = audio_file.replace(".wav", "_transcript.txt")
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(transcript)

            logger.info(f"Transcript saved: {transcript_file}")
            return transcript_file

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None

if __name__ == "__main__":
    transcriber = Transcriber()
    transcript = transcriber.transcribe('sample_audio.wav')
    if transcript:
        logger.info(f"Transcript created: {transcript}")
