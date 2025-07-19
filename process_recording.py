#!/usr/bin/env python3
"""
Process existing recording and organize into session directory
"""

import os
import shutil
from datetime import datetime
import whisper
import ollama
import logging

os.environ['TQDM_DISABLE'] = '1'

ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg', 'bin')
if os.path.exists(ffmpeg_path):
    current_path = os.environ.get('PATH', '')
    if ffmpeg_path not in current_path:
        os.environ['PATH'] = ffmpeg_path + os.pathsep + current_path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_recording(audio_file, video_file=None, session_name=None, recording_type="GoogleMeet", custom_name=None):
    """Process a recording and organize into session directory"""

    if not session_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if custom_name:
            session_name = f"{recording_type}_{custom_name}_{timestamp}"
        else:
            session_name = f"{recording_type}_{timestamp}"

    session_dir = os.path.join("sessions", session_name)
    os.makedirs(session_dir, exist_ok=True)
    logger.info(f"Created session directory: {session_dir}")

    new_audio_path = None
    new_video_path = None

    if audio_file and os.path.exists(audio_file):
        new_audio_path = os.path.join(session_dir, "audio.wav")
        shutil.move(audio_file, new_audio_path)
        logger.info(f"Moved audio: {audio_file} -> {new_audio_path}")

    if video_file and os.path.exists(video_file):
        new_video_path = os.path.join(session_dir, "video.avi")
        shutil.move(video_file, new_video_path)
        logger.info(f"Moved video: {video_file} -> {new_video_path}")

    video_transcript_path = None
    if new_video_path:
        logger.info("Extracting audio from video for transcription...")
        video_audio_path = extract_audio_from_video(new_video_path, session_dir)
        if video_audio_path:
            logger.info("Starting video audio transcription...")
            video_transcript_path = transcribe_audio(video_audio_path, session_dir, recording_type, source="video")

    mixed_transcript_path = None
    if new_audio_path:
        logger.info("Starting mixed audio transcription...")
        mixed_transcript_path = transcribe_audio(new_audio_path, session_dir, recording_type, source="mixed")

    primary_transcript_path = video_transcript_path or mixed_transcript_path

    summary_path = None
    if primary_transcript_path:
        logger.info("Generating summary...")
        with open(primary_transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
        summary_path = generate_summary(transcript, session_dir, recording_type)

    info_path = os.path.join(session_dir, "session_info.txt")
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(f"{recording_type} Recording Session\n")
        f.write(f"=" * 40 + "\n")
        f.write(f"Session: {session_name}\n")
        f.write(f"Type: {recording_type}\n")
        if custom_name:
            f.write(f"Name: {custom_name}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Audio: {'✅' if new_audio_path else '❌'}\n")
        f.write(f"Video: {'✅' if new_video_path else '❌'}\n")
        f.write(f"Video Transcript: {'✅' if video_transcript_path else '❌'}\n")
        f.write(f"Mixed Transcript: {'✅' if mixed_transcript_path else '❌'}\n")
        f.write(f"Primary Transcript: {'✅' if primary_transcript_path else '❌'}\n")
        f.write(f"Summary: {'✅' if summary_path else '❌'}\n")

    logger.info(f"Session processing completed: {session_dir}")
    return session_dir

def extract_audio_from_video(video_file, session_dir):
    """Extract audio from video file using FFmpeg"""
    try:
        import subprocess

        video_path = os.path.abspath(video_file)
        audio_output_path = os.path.join(session_dir, "video_audio.wav")

        logger.info(f"Extracting audio from video: {video_path}")

        ffmpeg_cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "2",
            "-y",
            audio_output_path
        ]
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            logger.info(f"✅ Audio extracted successfully: {audio_output_path}")
            return audio_output_path
        else:
            logger.error(f"FFmpeg extraction failed: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        logger.error("Audio extraction timed out (5 minutes)")
        return None
    except Exception as e:
        logger.error(f"Audio extraction error: {e}")
        return None

def transcribe_audio(audio_file, session_dir, recording_type="Recording", source="audio"):
    """Transcribe audio file"""
    try:
        audio_path = os.path.abspath(audio_file)
        logger.info(f"Loading Whisper model for file: {audio_path}")

        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return None

        model = whisper.load_model("base")

        logger.info("Transcribing audio...")
        result = model.transcribe(audio_path)
        transcript = result["text"]

        logger.info(f"Transcription completed. Length: {len(transcript)} characters")

        transcript_path = os.path.join(session_dir, "transcript.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(f"{recording_type} Transcript\n")
            f.write("=" * 40 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Audio file: {os.path.basename(audio_path)}\n\n")
            f.write(transcript)

        logger.info(f"Transcript saved: {transcript_path}")
        return transcript_path

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return None

def generate_summary(transcript, session_dir, recording_type="Recording"):
    """Generate content summary based on recording type"""
    try:
        if recording_type == "GoogleMeet":
            prompt = f"""
            Please analyze this Google Meet transcript and provide:
            1. A concise summary of the main topics discussed
            2. Key decisions made
            3. Action items and who they're assigned to
            4. Important points or insights shared

            Transcript:
            {transcript}

            Please format your response clearly with headers for each section.
            """
        elif recording_type == "Lesson":
            prompt = f"""
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
        elif recording_type == "Video":
            prompt = f"""
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
            prompt = f"""
            Please analyze this recording transcript and provide:
            1. A concise summary of the main content
            2. Key points or highlights
            3. Important information or insights
            4. Any actionable items mentioned

            Transcript:
            {transcript}

            Please format your response clearly with headers for each section.
            """

        logger.info("Connecting to Ollama...")
        response = ollama.chat(model="mistral", messages=[
            {'role': 'user', 'content': prompt}
        ])

        summary = response['message']['content']

        summary_path = os.path.join(session_dir, "summary.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(f"{recording_type} Summary\n")
            f.write("=" * 40 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(summary)

        logger.info(f"Summary saved: {summary_path}")
        return summary_path

    except Exception as e:
        logger.error(f"Summary generation error: {e}")
        return None

def get_recording_type_and_name():
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
                recording_type = "GoogleMeet"
                break
            elif choice == '2':
                recording_type = "Lesson"
                break
            elif choice == '3':
                recording_type = "Video"
                break
            else:
                print("❌ Invalid choice. Please select 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n\n❌ Process cancelled by user.")
            return None, None

    custom_name = None
    if recording_type in ["Lesson", "Video"]:
        print(f"\n📝 {recording_type} Name")
        while True:
            custom_name = input(f"Enter {recording_type.lower()} name (or press Enter to skip): ").strip()
            if custom_name:
                custom_name = "".join(c for c in custom_name if c.isalnum() or c in (' ', '-', '_')).strip()
                custom_name = custom_name.replace(' ', '_')
                if custom_name:
                    break
                print("❌ Invalid name. Please use only letters, numbers, spaces, hyphens, and underscores.")
            else:
                custom_name = None
                break

    return recording_type, custom_name

def main():
    """Process recording files"""
    import sys

    print("🎥 Recording Processor")
    print("=" * 50)

    if len(sys.argv) < 2:
        print("Usage: python process_recording.py <audio_file> [video_file] [recording_type] [custom_name]")
        print("\nExamples:")
        print("  python process_recording.py mixed_audio.wav dual_recording.avi GoogleMeet")
        print("  python process_recording.py lesson_audio.wav lesson_video.avi Lesson 'Python_Basics'")
        print("\nLooking for audio/video files in current directory...")

        import glob
        audio_files = glob.glob("*.wav") + glob.glob("*.mp3")
        video_files = glob.glob("*.avi") + glob.glob("*.mp4")

        if not audio_files:
            print("❌ No audio files found (.wav, .mp3)")
            return

        audio_file = audio_files[0]
        video_file = video_files[0] if video_files else None

        print(f"📁 Found audio: {audio_file}")
        if video_file:
            print(f"📁 Found video: {video_file}")

        recording_type, custom_name = get_recording_type_and_name()
        if recording_type is None:
            return

        session_name = None

    else:
        audio_file = sys.argv[1]
        video_file = sys.argv[2] if len(sys.argv) > 2 else None
        recording_type = sys.argv[3] if len(sys.argv) > 3 else "GoogleMeet"
        custom_name = sys.argv[4] if len(sys.argv) > 4 else None
        session_name = None

    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return

    if video_file and not os.path.exists(video_file):
        print(f"⚠️ Video file not found: {video_file}")
        video_file = None

    print(f"\n🔄 Processing {recording_type} Recording")
    if custom_name:
        print(f"📝 Name: {custom_name}")
    print("=" * 50)

    session_dir = process_recording(audio_file, video_file, session_name, recording_type, custom_name)

    print(f"\n✅ Processing completed!")
    print(f"📁 Session directory: {session_dir}")
    print(f"📄 Files:")

    for file in os.listdir(session_dir):
        file_path = os.path.join(session_dir, file)
        size = os.path.getsize(file_path)
        size_mb = size / (1024 * 1024)
        print(f"  - {file} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    main()
