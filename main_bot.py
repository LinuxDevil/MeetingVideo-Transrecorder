"""
Main bot script integrating dual audio recording, transcription, and AI summarization
"""

from src.audio_processing import AudioRecorder
from src.video_processing import VideoRecorder
from src.transcription import Transcriber
from src.summarization import Summarizer
from src.utils import get_recording_type_from_user, find_audio_video_files, RecordingType

import time
import logging

logger = logging.getLogger(__name__)

class DualAudioVideoBot:
    """Main bot orchestrating audio/video recording, transcription, and summarization"""
    
    def __init__(self):
        self.audio_recorder = AudioRecorder()
        self.video_recorder = VideoRecorder()
        self.transcriber = Transcriber()
        self.summarizer = Summarizer()

    def start(self):
        """Start the recording and processing flow"""
        logger.info("Starting Dual Audio Video Recording Bot")

        recording_type, custom_name = get_recording_type_from_user()
        if recording_type is None:
            return

        self.audio_recorder.find_audio_devices()
        self.video_recorder.screen_size = self.video_recorder.get_screen_region_interactively()  # Adjust screen region if needed

        audio_filename = self.audio_recorder.start_recording()
        video_filename = self.video_recorder.start_recording()

        logger.info("Recording started. Use Ctrl+C to stop.")

        try:
            while True:
                time.sleep(1)  # Keep recording
        except KeyboardInterrupt:
            audio_file = self.audio_recorder.stop_recording()
            self.video_recorder.stop_recording()

            if audio_file:
                logger.info("Processing recordings...")
                self.process_recordings(audio_file, video_filename, recording_type)

    def process_recordings(self, audio_file: str, video_file: str, recording_type: RecordingType):
        """Process audio and video recordings for transcription and summarization"""
        # Transcribe audio
        transcript_file = self.transcriber.transcribe(audio_file)

        # Summarize transcript
        if transcript_file:
            with open(transcript_file, 'r', encoding='utf-8') as f:
                transcript = f.read()
            self.summarizer.generate_summary(transcript, recording_type)

# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    bot = DualAudioVideoBot()
    bot.start()
