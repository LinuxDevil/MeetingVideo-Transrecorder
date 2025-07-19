"""
Configuration management for the recording bot
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class AudioConfig:
    """Audio recording configuration"""
    sample_rate: int = 44100
    chunk_size: int = 1024
    format_bits: int = 16
    channels: int = 2
    system_audio_volume: float = 0.7
    microphone_volume: float = 0.3
    microphone_reduction_db: int = 6

@dataclass
class VideoConfig:
    """Video recording configuration"""
    fps: int = 20
    codec: str = "XVID"
    extension: str = "avi"

@dataclass
class WhisperConfig:
    """Whisper transcription configuration"""
    model_size: str = "base"
    language: Optional[str] = None
    task: str = "transcribe"

@dataclass
class OllamaConfig:
    """Ollama AI configuration"""
    model: str = "mistral"
    host: str = "localhost"
    port: int = 11434

@dataclass
class PathsConfig:
    """File and directory paths configuration"""
    sessions_dir: str = "sessions"
    ffmpeg_dir: str = "ffmpeg"
    temp_dir: str = "temp"

    def __post_init__(self):
        """Create directories if they don't exist"""
        for dir_path in [self.sessions_dir, self.temp_dir]:
            os.makedirs(dir_path, exist_ok=True)

@dataclass
class Config:
    """Main configuration class"""
    audio: AudioConfig = AudioConfig()
    video: VideoConfig = VideoConfig()
    whisper: WhisperConfig = WhisperConfig()
    ollama: OllamaConfig = OllamaConfig()
    paths: PathsConfig = PathsConfig()
    disable_tqdm: bool = True
    log_level: str = "INFO"

    def __post_init__(self):
        """Setup environment variables and paths"""
        if self.disable_tqdm:
            os.environ['TQDM_DISABLE'] = '1'

        ffmpeg_path = os.path.join(os.getcwd(), self.paths.ffmpeg_dir, 'bin')
        if os.path.exists(ffmpeg_path):
            current_path = os.environ.get('PATH', '')
            if ffmpeg_path not in current_path:
                os.environ['PATH'] = ffmpeg_path + os.pathsep + current_path

config = Config()
