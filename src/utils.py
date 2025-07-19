"""
Utility functions and common functionality
"""

import os
import logging
from datetime import datetime
from typing import Tuple, Optional, List
from enum import Enum

class RecordingType(Enum):
    """Supported recording types"""
    GOOGLE_MEET = "GoogleMeet"
    LESSON = "Lesson"
    VIDEO = "Video"

def setup_logging(level: str = "INFO", format_str: Optional[str] = None) -> logging.Logger:
    """Setup logging configuration"""
    if format_str is None:
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_str,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    return logging.getLogger(__name__)

def generate_timestamp() -> str:
    """Generate timestamp string for file naming"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def sanitize_filename(name: str) -> str:
    """Sanitize a string for use as filename"""
    if not name:
        return None

    sanitized = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    sanitized = sanitized.replace(' ', '_')

    return sanitized if sanitized else None

def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes"""
    if not os.path.exists(file_path):
        return 0.0

    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)

def create_session_name(recording_type: RecordingType, custom_name: Optional[str] = None) -> str:
    """Create session directory name"""
    timestamp = generate_timestamp()

    if custom_name:
        sanitized_name = sanitize_filename(custom_name)
        return f"{recording_type.value}_{sanitized_name}_{timestamp}"
    else:
        return f"{recording_type.value}_{timestamp}"

def get_recording_type_from_user() -> Tuple[Optional[RecordingType], Optional[str]]:
    """Interactive function to get recording type and custom name"""
    print("\n🎥 Recording Type Selection")
    print("=" * 30)
    print("1. Google Meet")
    print("2. Lesson")
    print("3. Video")

    while True:
        try:
            choice = input("\nSelect recording type (1-3): ").strip()
            if choice == '1':
                recording_type = RecordingType.GOOGLE_MEET
                break
            elif choice == '2':
                recording_type = RecordingType.LESSON
                break
            elif choice == '3':
                recording_type = RecordingType.VIDEO
                break
            else:
                print("❌ Invalid choice. Please select 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n\n❌ Process cancelled by user.")
            return None, None

    custom_name = None
    if recording_type in [RecordingType.LESSON, RecordingType.VIDEO]:
        print(f"\n📝 {recording_type.value} Name")
        while True:
            custom_name = input(f"Enter {recording_type.value.lower()} name (or press Enter to skip): ").strip()
            if custom_name:
                custom_name = sanitize_filename(custom_name)
                if custom_name:
                    break
                print("❌ Invalid name. Please use only letters, numbers, spaces, hyphens, and underscores.")
            else:
                custom_name = None
                break

    return recording_type, custom_name

def find_audio_video_files() -> Tuple[Optional[str], Optional[str]]:
    """Find audio and video files in current directory"""
    import glob

    audio_files = glob.glob("*.wav") + glob.glob("*.mp3")
    video_files = glob.glob("*.avi") + glob.glob("*.mp4")

    audio_file = audio_files[0] if audio_files else None
    video_file = video_files[0] if video_files else None

    return audio_file, video_file

def list_directory_files(directory: str) -> List[Tuple[str, float]]:
    """List files in directory with their sizes in MB"""
    files = []
    if not os.path.exists(directory):
        return files

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            size_mb = get_file_size_mb(file_path)
            files.append((filename, size_mb))

    return files
