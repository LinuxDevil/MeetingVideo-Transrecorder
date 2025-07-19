"""
AI Summarization module using Ollama
"""

import ollama
from typing import Optional
from datetime import datetime
from src.config import config
from src.utils import setup_logging, RecordingType

logger = setup_logging(level=config.log_level)

class Summarizer:
    """Ollama AI summarization handler"""

    def __init__(self):
        self.model = config.ollama.model
        self._check_ollama_connection()

    def _check_ollama_connection(self):
        """Check if Ollama is running and pull model if needed"""
        try:
            models = ollama.list()
            logger.info("Ollama is running")
            model_names = [model.model for model in models['models']]
            if not any('llama2' in name.lower() or 'mistral' in name.lower() for name in model_names):
                logger.info("Pulling Mistral model...")
                ollama.pull(self.model)
        except Exception as e:
            logger.error(f"Ollama error: {e}")

    def generate_summary(self, transcript: str, recording_type: RecordingType) -> Optional[str]:
        """Generate AI summary based on recording type"""
        logger.info(f"Generating {recording_type.value} summary...")

        prompt = self._get_prompt_for_type(recording_type, transcript)

        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt}
            ])

            summary = response['message']['content']

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = f"{recording_type.value.lower()}_summary_{timestamp}.txt"

            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(f"# {recording_type.value} Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(summary)

            logger.info(f"Summary saved: {summary_file}")
            return summary_file

        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return None

    def _get_prompt_for_type(self, recording_type: RecordingType, transcript: str) -> str:
        """Get appropriate prompt based on recording type"""

        if recording_type == RecordingType.GOOGLE_MEET:
            return f"""
            Please analyze this Google Meet transcript and provide:
            1. A concise summary of the main topics discussed
            2. Key decisions made
            3. Action items and who they're assigned to
            4. Important points or insights shared

            Transcript:
            {transcript}

            Please format your response clearly with headers for each section.
            """

        elif recording_type == RecordingType.LESSON:
            return f"""
            Please analyze this lesson transcript and provide:
            1. A summary of the main learning objectives
            2. Key concepts and topics covered
            3. Important definitions or explanations
            4. Practical examples or demonstrations mentioned
            5. Assignments or homework given

            Transcript:
            {transcript}

            Please format your response clearly with headers for each section.
            """

        elif recording_type == RecordingType.VIDEO:
            return f"""
            Please analyze this video transcript and provide:
            1. A concise summary of the main content
            2. Key points or highlights
            3. Important information or insights
            4. Any actionable items mentioned

            Transcript:
            {transcript}

            Please format your response clearly with headers for each section.
            """

        else:
            return f"""
            Please analyze this recording transcript and provide:
            1. A concise summary of the main content
            2. Key points or highlights
            3. Important information or insights
            4. Any actionable items mentioned

            Transcript:
            {transcript}

            Please format your response clearly with headers for each section.
            """

if __name__ == "__main__":
    summarizer = Summarizer()
    sample_transcript = "This is a sample transcript for testing."
    summary_file = summarizer.generate_summary(sample_transcript, RecordingType.GOOGLE_MEET)
    if summary_file:
        logger.info(f"Summary created: {summary_file}")
