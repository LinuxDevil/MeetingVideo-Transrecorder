#!/usr/bin/env python3
"""
Test script for refactored components
"""

import sys
import os

def test_imports():
    """Test if all refactored modules can be imported"""
    print("Testing refactored module imports...")
    
    try:
        from src.config import config
        print("✅ Config module imported successfully")
    except ImportError as e:
        print(f"❌ Config module import failed: {e}")
        return False
    
    try:
        from src.utils import RecordingType, setup_logging
        print("✅ Utils module imported successfully")
    except ImportError as e:
        print(f"❌ Utils module import failed: {e}")
        return False
    
    try:
        from src.audio_processing import AudioRecorder
        print("✅ Audio processing module imported successfully")
    except ImportError as e:
        print(f"❌ Audio processing module import failed: {e}")
    
    try:
        from src.video_processing import VideoRecorder
        print("✅ Video processing module imported successfully")
    except ImportError as e:
        print(f"❌ Video processing module import failed: {e}")
    
    try:
        from src.transcription import Transcriber
        print("✅ Transcription module imported successfully")
    except ImportError as e:
        print(f"❌ Transcription module import failed: {e}")
    
    try:
        from src.summarization import Summarizer
        print("✅ Summarization module imported successfully")
    except ImportError as e:
        print(f"❌ Summarization module import failed: {e}")
    
    try:
        from src.session_manager import SessionManager
        print("✅ Session manager module imported successfully")
    except ImportError as e:
        print(f"❌ Session manager module import failed: {e}")
    
    return True

def test_config():
    """Test configuration module"""
    print("\nTesting configuration...")
    
    from src.config import config
    
    print(f"📊 Audio sample rate: {config.audio.sample_rate} Hz")
    print(f"🎥 Video FPS: {config.video.fps}")
    print(f"🤖 Whisper model: {config.whisper.model_size}")
    print(f"🧠 Ollama model: {config.ollama.model}")
    print(f"📁 Sessions directory: {config.paths.sessions_dir}")
    
    # Check if directories were created
    if os.path.exists(config.paths.sessions_dir):
        print(f"✅ Sessions directory created: {config.paths.sessions_dir}")
    else:
        print(f"❌ Sessions directory not created: {config.paths.sessions_dir}")

def test_utils():
    """Test utility functions"""
    print("\nTesting utilities...")
    
    from src.utils import RecordingType, sanitize_filename, generate_timestamp, create_session_name
    
    # Test recording types
    print(f"📝 Recording types: {[rt.value for rt in RecordingType]}")
    
    # Test filename sanitization
    test_names = ["Test Meeting!", "Lesson #1: Python", "Video@Home", ""]
    for name in test_names:
        sanitized = sanitize_filename(name)
        print(f"   '{name}' -> '{sanitized}'")
    
    # Test timestamp generation
    timestamp = generate_timestamp()
    print(f"⏰ Generated timestamp: {timestamp}")
    
    # Test session name creation
    session_name = create_session_name(RecordingType.LESSON, "Python Basics")
    print(f"📂 Session name: {session_name}")

def test_session_manager():
    """Test session manager functionality"""
    print("\nTesting session manager...")
    
    from src.session_manager import SessionManager
    from src.utils import RecordingType
    
    session_manager = SessionManager()
    
    # List existing sessions
    sessions = session_manager.list_sessions()
    print(f"📁 Found {len(sessions)} existing sessions")
    
    print("✅ Session manager tested successfully")

def test_audio_devices():
    """Test audio device detection"""
    print("\nTesting audio device detection...")
    
    try:
        from src.audio_processing import AudioRecorder
        
        recorder = AudioRecorder()
        recorder.find_audio_devices()
        
        if recorder.system_audio_device is not None:
            print(f"✅ System audio device found: {recorder.system_device_info['name']}")
        else:
            print("⚠️ No system audio device found")
            
        if recorder.mic_device is not None:
            print(f"✅ Microphone device found: {recorder.mic_device_info['name']}")
        else:
            print("⚠️ No microphone device found")
            
        recorder.cleanup()
        
    except Exception as e:
        print(f"❌ Audio device test failed: {e}")

def test_ollama_connection():
    """Test Ollama connection"""
    print("\nTesting Ollama connection...")
    
    try:
        from src.summarization import Summarizer
        
        summarizer = Summarizer()
        print("✅ Ollama summarizer initialized successfully")
        
    except Exception as e:
        print(f"❌ Ollama connection test failed: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing Refactored Recording Bot Components")
    print("=" * 60)
    
    if not test_imports():
        print("\n❌ Module import tests failed. Check dependencies.")
        return
    
    test_config()
    test_utils()
    test_session_manager()
    test_audio_devices()
    test_ollama_connection()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    
    print("\nNext steps:")
    print("1. Run the refactored bot: python dual_audio_bot_refactored.py")
    print("2. Use CLI tools: python cli_tools.py list")
    print("3. Process existing files: python cli_tools.py auto")

if __name__ == "__main__":
    main()
