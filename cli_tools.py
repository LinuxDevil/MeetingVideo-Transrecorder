#!/usr/bin/env python3
"""
Command-line tools for managing sessions and processing recordings
"""

import argparse
import sys
from typing import Optional

from src.session_manager import SessionManager
from src.transcription import Transcriber
from src.summarization import Summarizer
from src.utils import RecordingType, find_audio_video_files, setup_logging
from src.config import config

logger = setup_logging(level=config.log_level)

def list_sessions():
    """List all recording sessions"""
    session_manager = SessionManager()
    sessions = session_manager.list_sessions()
    
    if not sessions:
        print("📭 No sessions found.")
        return
    
    print(f"📁 Found {len(sessions)} recording sessions:")
    print("=" * 60)
    
    for session in sessions:
        info = session['info']
        print(f"🎥 {info['recording_type']}: {session['name']}")
        print(f"   📅 Created: {info['created_at'][:19]}")
        if info.get('custom_name'):
            print(f"   📝 Name: {info['custom_name']}")
        
        # Show file sizes
        sizes = info.get('file_sizes_mb', {})
        size_str = ", ".join([f"{k}: {v}MB" for k, v in sizes.items() if v])
        if size_str:
            print(f"   💾 Files: {size_str}")
        print()

def process_existing_recording(audio_file: str, video_file: Optional[str] = None, 
                             recording_type: str = "GoogleMeet", custom_name: Optional[str] = None):
    """Process existing recording files"""
    print("🔄 Processing existing recording...")
    
    try:
        rec_type = RecordingType(recording_type)
    except ValueError:
        print(f"❌ Invalid recording type: {recording_type}")
        print(f"Available types: {', '.join([rt.value for rt in RecordingType])}")
        return
    
    # Initialize components
    session_manager = SessionManager()
    transcriber = Transcriber()
    summarizer = Summarizer()
    
    # Create session
    session_path = session_manager.create_session(rec_type, custom_name)
    
    # Transcribe audio
    transcript_file = transcriber.transcribe(audio_file)
    
    # Generate summary
    summary_file = None
    if transcript_file:
        with open(transcript_file, 'r', encoding='utf-8') as f:
            transcript = f.read()
        summary_file = summarizer.generate_summary(transcript, rec_type)
    
    # Organize files
    organized_files = session_manager.organize_files(
        session_path, audio_file, video_file, transcript_file, summary_file
    )
    
    # Create session info
    session_manager.create_session_info(session_path, rec_type, custom_name, organized_files)
    
    # Print summary
    session_manager.print_session_summary(session_path)
    print("\n✅ Processing completed!")

def delete_session(session_name: str):
    """Delete a recording session"""
    session_manager = SessionManager()
    sessions = session_manager.list_sessions()
    
    # Find matching session
    target_session = None
    for session in sessions:
        if session['name'] == session_name:
            target_session = session
            break
    
    if not target_session:
        print(f"❌ Session not found: {session_name}")
        print("Available sessions:")
        for session in sessions:
            print(f"  - {session['name']}")
        return
    
    # Confirm deletion
    print(f"🗑️ Delete session: {session_name}")
    confirm = input("Are you sure? (y/N): ").strip().lower()
    
    if confirm == 'y':
        import shutil
        shutil.rmtree(target_session['path'])
        print(f"✅ Session deleted: {session_name}")
    else:
        print("❌ Deletion cancelled")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Recording Bot CLI Tools")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List sessions command
    list_parser = subparsers.add_parser('list', help='List all recording sessions')
    
    # Process recording command
    process_parser = subparsers.add_parser('process', help='Process existing recording files')
    process_parser.add_argument('audio_file', help='Audio file path')
    process_parser.add_argument('--video', help='Video file path (optional)')
    process_parser.add_argument('--type', choices=[rt.value for rt in RecordingType], 
                               default='GoogleMeet', help='Recording type')
    process_parser.add_argument('--name', help='Custom name for the recording')
    
    # Delete session command
    delete_parser = subparsers.add_parser('delete', help='Delete a recording session')
    delete_parser.add_argument('session_name', help='Name of the session to delete')
    
    # Auto-process command
    auto_parser = subparsers.add_parser('auto', help='Auto-process files in current directory')
    auto_parser.add_argument('--type', choices=[rt.value for rt in RecordingType], 
                           default='GoogleMeet', help='Recording type')
    auto_parser.add_argument('--name', help='Custom name for the recording')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_sessions()
        
    elif args.command == 'process':
        process_existing_recording(args.audio_file, args.video, args.type, args.name)
        
    elif args.command == 'delete':
        delete_session(args.session_name)
        
    elif args.command == 'auto':
        audio_file, video_file = find_audio_video_files()
        if not audio_file:
            print("❌ No audio files found (.wav, .mp3)")
            return
        
        print(f"📁 Found audio: {audio_file}")
        if video_file:
            print(f"📁 Found video: {video_file}")
        
        process_existing_recording(audio_file, video_file, args.type, args.name)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
