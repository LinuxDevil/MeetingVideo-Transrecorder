"""
Session management for organizing recordings
"""

import os
import shutil
import json
from datetime import datetime
from typing import Optional, Dict, Any
from src.config import config
from src.utils import setup_logging, RecordingType, create_session_name, list_directory_files

logger = setup_logging(level=config.log_level)

class SessionManager:
    """Manage recording sessions and organization"""

    def __init__(self):
        self.sessions_dir = config.paths.sessions_dir

    def create_session(self, recording_type: RecordingType, custom_name: Optional[str] = None) -> str:
        """Create a new session directory"""
        session_name = create_session_name(recording_type, custom_name)
        session_path = os.path.join(self.sessions_dir, session_name)
        os.makedirs(session_path, exist_ok=True)

        logger.info(f"Created session directory: {session_path}")
        return session_path

    def organize_files(self, session_path: str, audio_file: Optional[str], video_file: Optional[str],
                      transcript_file: Optional[str], summary_file: Optional[str]) -> Dict[str, Optional[str]]:
        """Move and organize files into session directory"""
        organized_files = {
            'audio': None,
            'video': None,
            'transcript': None,
            'summary': None
        }

        if audio_file and os.path.exists(audio_file):
            new_audio_path = os.path.join(session_path, "audio.wav")
            shutil.move(audio_file, new_audio_path)
            organized_files['audio'] = new_audio_path
            logger.info(f"Moved audio: {audio_file} -> {new_audio_path}")

        if video_file and os.path.exists(video_file):
            video_ext = os.path.splitext(video_file)[1]
            new_video_path = os.path.join(session_path, f"video{video_ext}")
            shutil.move(video_file, new_video_path)
            organized_files['video'] = new_video_path
            logger.info(f"Moved video: {video_file} -> {new_video_path}")

        if transcript_file and os.path.exists(transcript_file):
            new_transcript_path = os.path.join(session_path, "transcript.txt")
            shutil.move(transcript_file, new_transcript_path)
            organized_files['transcript'] = new_transcript_path
            logger.info(f"Moved transcript: {transcript_file} -> {new_transcript_path}")

        if summary_file and os.path.exists(summary_file):
            new_summary_path = os.path.join(session_path, "summary.txt")
            shutil.move(summary_file, new_summary_path)
            organized_files['summary'] = new_summary_path
            logger.info(f"Moved summary: {summary_file} -> {new_summary_path}")

        return organized_files

    def create_session_info(self, session_path: str, recording_type: RecordingType,
                          custom_name: Optional[str], organized_files: Dict[str, Optional[str]]):
        """Create session info file with metadata"""
        session_name = os.path.basename(session_path)

        session_info = {
            'session_name': session_name,
            'recording_type': recording_type.value,
            'custom_name': custom_name,
            'created_at': datetime.now().isoformat(),
            'files': {
                'audio': os.path.basename(organized_files['audio']) if organized_files['audio'] else None,
                'video': os.path.basename(organized_files['video']) if organized_files['video'] else None,
                'transcript': os.path.basename(organized_files['transcript']) if organized_files['transcript'] else None,
                'summary': os.path.basename(organized_files['summary']) if organized_files['summary'] else None,
            },
            'file_sizes_mb': {}
        }

        for file_type, file_path in organized_files.items():
            if file_path and os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                session_info['file_sizes_mb'][file_type] = round(size_bytes / (1024 * 1024), 2)

        info_path = os.path.join(session_path, "session_info.json")
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(session_info, f, indent=2, ensure_ascii=False)

        logger.info(f"Session info saved: {info_path}")

    def list_sessions(self) -> list:
        """List all session directories"""
        if not os.path.exists(self.sessions_dir):
            return []

        sessions = []
        for item in os.listdir(self.sessions_dir):
            session_path = os.path.join(self.sessions_dir, item)
            if os.path.isdir(session_path):
                info_file = os.path.join(session_path, "session_info.json")
                if os.path.exists(info_file):
                    try:
                        with open(info_file, 'r', encoding='utf-8') as f:
                            session_info = json.load(f)
                        sessions.append({
                            'path': session_path,
                            'name': item,
                            'info': session_info
                        })
                    except Exception as e:
                        logger.warning(f"Could not read session info for {item}: {e}")

        return sorted(sessions, key=lambda x: x['info'].get('created_at', ''), reverse=True)

    def print_session_summary(self, session_path: str):
        """Print summary of session contents"""
        session_name = os.path.basename(session_path)
        print(f"\n✅ Session: {session_name}")
        print("=" * 60)

        files = list_directory_files(session_path)
        for filename, size_mb in files:
            print(f"  📄 {filename} ({size_mb:.1f} MB)")

        print(f"📁 Location: {session_path}")

if __name__ == "__main__":
    session_manager = SessionManager()
    session_path = session_manager.create_session(RecordingType.GOOGLE_MEET, "Test Meeting")
    logger.info(f"Created test session: {session_path}")

    sessions = session_manager.list_sessions()
    print(f"Found {len(sessions)} sessions")
