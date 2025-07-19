#!/usr/bin/env python3
"""
Refactored Dual Audio Recording Bot
Modular implementation with improved structure and maintainability
"""

import time
from typing import Optional, Tuple

from src.audio_processing import AudioRecorder
from src.video_processing import VideoRecorder
from src.transcription import Transcriber
from src.summarization import Summarizer
from src.session_manager import SessionManager
from src.utils import get_recording_type_from_user, RecordingType, setup_logging
from src.config import config

logger = setup_logging(level=config.log_level)

class DualAudioBot:
    """
    Enhanced dual audio recording bot with modular components
    """
    
    def __init__(self):
        self.audio_recorder = AudioRecorder()
        self.video_recorder = VideoRecorder()
        self.transcriber = Transcriber()
        self.summarizer = Summarizer()
        self.session_manager = SessionManager()
        
    def start_interactive_recording(self):
        """Start interactive recording session"""
        print("🎥🎤 Dual Audio Google Meet Recording Bot")
        print("=" * 60)
        print("Records BOTH system audio (others) AND microphone (you)")
        print("=" * 60)

        # Get recording type and name
        recording_type, custom_name = get_recording_type_from_user()
        if recording_type is None:
            return

        # Setup audio devices
        self.audio_recorder.find_audio_devices()

        print("\nOptions:")
        print("1. Record full meeting (system audio + microphone + screen)")
        print("2. Record specific screen region")
        print("3. Manual control (start/stop)")
        print("0. Exit")

        try:
            while True:
                choice = input("\nSelect option (0-3): ").strip()

                if choice == "0":
                    print("Goodbye! 👋")
                    break

                elif choice == "1":
                    self._handle_full_recording(recording_type, custom_name)

                elif choice == "2":
                    self._handle_region_recording(recording_type, custom_name)

                elif choice == "3":
                    self._handle_manual_recording(recording_type, custom_name)

                else:
                    print("❌ Invalid option. Please select 0-3.")

        finally:
            self.cleanup()

    def _handle_full_recording(self, recording_type: RecordingType, custom_name: Optional[str]):
        """Handle full screen recording"""
        duration = input("Enter duration in minutes (default 60): ").strip()
        
        try:
            duration = int(duration) if duration else 60
            print(f"\n🎬 Starting DUAL audio recording for {duration} minutes...")
            print("📺 Screen: Full screen")
            print("🔊 System audio: Meeting voices")
            print("🎤 Microphone: Your voice")
            print("\nPress Ctrl+C to stop early")

            # Start recording
            self.audio_recorder.start_recording()
            video_filename = self.video_recorder.start_recording()
            
            time.sleep(duration * 60)
            
            # Stop recording and process
            audio_file = self.audio_recorder.stop_recording()
            self.video_recorder.stop_recording()
            
            if audio_file:
                self._process_and_organize(audio_file, video_filename, recording_type, custom_name)

        except ValueError:
            print("❌ Invalid duration")
        except KeyboardInterrupt:
            print("\n⏹️ Stopping recording...")
            audio_file = self.audio_recorder.stop_recording()
            self.video_recorder.stop_recording()
            
            if audio_file:
                self._process_and_organize(audio_file, video_filename, recording_type, custom_name)

    def _handle_region_recording(self, recording_type: RecordingType, custom_name: Optional[str]):
        """Handle region-specific recording"""
        region = self.video_recorder.get_screen_region_interactively()
        if region is None:
            return
            
        duration = input("Enter duration in minutes (default 60): ").strip()
        
        try:
            duration = int(duration) if duration else 60
            print(f"\n🎬 Starting region recording for {duration} minutes...")
            print(f"📺 Region: {region}")
            print("🔊 System audio + 🎤 Microphone")

            # Start recording
            self.audio_recorder.start_recording()
            video_filename = self.video_recorder.start_recording(region=region)
            
            time.sleep(duration * 60)
            
            # Stop recording and process
            audio_file = self.audio_recorder.stop_recording()
            self.video_recorder.stop_recording()
            
            if audio_file:
                self._process_and_organize(audio_file, video_filename, recording_type, custom_name)

        except ValueError:
            print("❌ Invalid input")
        except KeyboardInterrupt:
            self.audio_recorder.stop_recording()
            self.video_recorder.stop_recording()

    def _handle_manual_recording(self, recording_type: RecordingType, custom_name: Optional[str]):
        """Handle manual recording control"""
        print("\n🎛️ Manual Control Mode")
        print("Commands: 'start', 'stop', 'quit'")

        audio_file = None
        video_filename = None
        
        while True:
            command = input("\nEnter command: ").strip().lower()

            if command == 'start':
                if not self.audio_recorder.recording:
                    self.audio_recorder.start_recording()
                    video_filename = self.video_recorder.start_recording()
                    print("✅ DUAL recording started!")
                    print("🔊 System audio + 🎤 Microphone + 📺 Screen")
                else:
                    print("⚠️ Already recording!")

            elif command == 'stop':
                if self.audio_recorder.recording:
                    audio_file = self.audio_recorder.stop_recording()
                    self.video_recorder.stop_recording()
                    
                    if audio_file:
                        self._process_and_organize(audio_file, video_filename, recording_type, custom_name)
                else:
                    print("⚠️ Not recording!")

            elif command == 'quit':
                if self.audio_recorder.recording:
                    self.audio_recorder.stop_recording()
                    self.video_recorder.stop_recording()
                break

            else:
                print("❌ Unknown command. Use 'start', 'stop', or 'quit'")

    def _process_and_organize(self, audio_file: str, video_filename: str, 
                            recording_type: RecordingType, custom_name: Optional[str]):
        """Process recordings and organize into session"""
        print("\n🔄 Organizing session and processing...")
        
        # Create session
        session_path = self.session_manager.create_session(recording_type, custom_name)
        
        # Transcribe audio
        transcript_file = self.transcriber.transcribe(audio_file)
        
        # Generate summary
        summary_file = None
        if transcript_file:
            with open(transcript_file, 'r', encoding='utf-8') as f:
                transcript = f.read()
            summary_file = self.summarizer.generate_summary(transcript, recording_type)
        
        # Organize files
        video_file = f"{video_filename}.{config.video.extension}" if video_filename else None
        organized_files = self.session_manager.organize_files(
            session_path, audio_file, video_file, transcript_file, summary_file
        )
        
        # Create session info
        self.session_manager.create_session_info(session_path, recording_type, custom_name, organized_files)
        
        # Print summary
        self.session_manager.print_session_summary(session_path)
        print("\n✅ Session processed successfully!")

    def cleanup(self):
        """Clean up resources"""
        try:
            self.audio_recorder.cleanup()
            logger.info("Resources cleaned up")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

def main():
    """Main function"""
    bot = DualAudioBot()
    bot.start_interactive_recording()

if __name__ == "__main__":
    main()
