#!/usr/bin/env python3
"""
Dual Audio Recording Bot for Google Meet
Records both system audio (others) and microphone (you) simultaneously
"""

import cv2
import numpy as np
import pyautogui
import time
import threading
import os
import pyaudio
import wave
from datetime import datetime
import whisper
import ollama
from pydub import AudioSegment
import logging
import shutil

os.environ['TQDM_DISABLE'] = '1'

ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg', 'bin')
if os.path.exists(ffmpeg_path):
    current_path = os.environ.get('PATH', '')
    if ffmpeg_path not in current_path:
        os.environ['PATH'] = ffmpeg_path + os.pathsep + current_path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DualAudioRecorder:
    def __init__(self, fps=20, audio_sample_rate=44100):
        """
        Initialize the dual audio recorder
        """
        self.fps = fps
        self.audio_sample_rate = audio_sample_rate
        self.recording = False
        self.screen_size = None
        self.video_writer = None

        self.system_audio_frames = []
        self.mic_audio_frames = []

        logger.info("Loading Whisper model for transcription...")
        self.whisper_model = whisper.load_model("base")
        self.check_ollama()
        self.screen_size = pyautogui.size()
        logger.info(f"Screen size detected: {self.screen_size}")

        self.audio = pyaudio.PyAudio()
        self.find_audio_devices()

    def check_ollama(self):
        """Check if Ollama is running"""
        try:
            models = ollama.list()
            logger.info("Ollama is running")
            model_names = [model.model for model in models['models']]
            if not any('llama2' in name.lower() or 'mistral' in name.lower() for name in model_names):
                logger.info("Pulling Mistral model...")
                ollama.pull('mistral')
        except Exception as e:
            logger.error(f"Ollama error: {e}")

    def find_audio_devices(self):
        """Find system audio and microphone devices"""
        logger.info("Scanning for audio devices...")

        self.system_audio_device = None
        self.mic_device = None
        self.system_device_info = None
        self.mic_device_info = None

        system_keywords = ['stereo mix', 'what you hear', 'wave out mix', 'loopback', 'monitor']
        mic_keywords = ['microphone', 'mic', 'hyperx', 'webcam', 'camera', 'headset', 'array']
        system_candidates = []
        mic_candidates = []

        try:
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    device_name = device_info['name'].lower()
                    logger.info(f"  {i}: {device_info['name']} (channels: {device_info['maxInputChannels']})")
                    if any(keyword in device_name for keyword in system_keywords):
                        system_candidates.append((i, device_info))
                        logger.info(f"    → System audio candidate")
                    elif any(keyword in device_name for keyword in mic_keywords):
                        mic_candidates.append((i, device_info))
                        logger.info(f"    → Microphone candidate")

            if system_candidates:
                for i, device_info in system_candidates:
                    if 'stereo mix' in device_info['name'].lower():
                        self.system_audio_device = i
                        self.system_device_info = device_info
                        break
                else:
                    self.system_audio_device = system_candidates[0][0]
                    self.system_device_info = system_candidates[0][1]

                logger.info(f"✅ Selected system audio: {self.system_device_info['name']}")

            if mic_candidates:
                for i, device_info in mic_candidates:
                    if 'hyperx' in device_info['name'].lower():
                        self.mic_device = i
                        self.mic_device_info = device_info
                        break
                else:
                    self.mic_device = mic_candidates[0][0]
                    self.mic_device_info = mic_candidates[0][1]

                logger.info(f"✅ Selected microphone: {self.mic_device_info['name']}")
            if self.system_audio_device is None:
                logger.warning("⚠️ No system audio device found!")
                logger.warning("Enable 'Stereo Mix' in Windows Sound settings")
            if self.mic_device is None:
                logger.warning("⚠️ No microphone found!")

        except Exception as e:
            logger.error(f"Error scanning devices: {e}")

    def start_recording(self, output_filename=None, region=None):
        """Start dual audio + screen recording"""
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"dual_recording_{timestamp}"

        self.recording = True
        self.system_audio_frames = []
        self.mic_audio_frames = []

        if region:
            x, y, width, height = region
            video_size = (width, height)
        else:
            x, y = 0, 0
            width, height = self.screen_size
            video_size = self.screen_size

        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        video_filename = f"{output_filename}.avi"
        self.video_writer = cv2.VideoWriter(video_filename, fourcc, self.fps, video_size)

        logger.info(f"Starting screen recording to {video_filename}")

        self.start_system_audio_recording()
        self.start_microphone_recording()

        def record_screen():
            try:
                while self.recording:
                    if region:
                        screenshot = pyautogui.screenshot(region=(x, y, width, height))
                    else:
                        screenshot = pyautogui.screenshot()

                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    self.video_writer.write(frame)
                    time.sleep(1/self.fps)

            except Exception as e:
                logger.error(f"Screen recording error: {e}")

        self.screen_thread = threading.Thread(target=record_screen)
        self.screen_thread.start()

        logger.info("✅ Dual recording started!")
        return output_filename

    def start_system_audio_recording(self):
        """Record system audio (what you hear)"""
        if self.system_audio_device is None:
            logger.warning("No system audio device - skipping")
            return

        def record_system():
            try:
                chunk = 1024
                format = pyaudio.paInt16
                channels = min(2, self.system_device_info['maxInputChannels'])

                logger.info(f"Recording system audio: {channels} channels")

                stream = self.audio.open(
                    format=format,
                    channels=channels,
                    rate=self.audio_sample_rate,
                    input=True,
                    input_device_index=self.system_audio_device,
                    frames_per_buffer=chunk
                )

                while self.recording:
                    try:
                        data = stream.read(chunk, exception_on_overflow=False)
                        self.system_audio_frames.append(data)
                    except Exception as e:
                        logger.error(f"System audio read error: {e}")
                        break

                stream.stop_stream()
                stream.close()
                logger.info("System audio recording stopped")

            except Exception as e:
                logger.error(f"System audio recording error: {e}")

        self.system_audio_thread = threading.Thread(target=record_system)
        self.system_audio_thread.start()

    def start_microphone_recording(self):
        """Record microphone (your voice)"""
        if self.mic_device is None:
            logger.warning("No microphone device - skipping")
            return

        def record_mic():
            try:
                chunk = 1024
                format = pyaudio.paInt16
                channels = min(2, self.mic_device_info['maxInputChannels'])

                logger.info(f"Recording microphone: {channels} channels")

                stream = self.audio.open(
                    format=format,
                    channels=channels,
                    rate=self.audio_sample_rate,
                    input=True,
                    input_device_index=self.mic_device,
                    frames_per_buffer=chunk
                )

                while self.recording:
                    try:
                        data = stream.read(chunk, exception_on_overflow=False)
                        self.mic_audio_frames.append(data)
                    except Exception as e:
                        logger.error(f"Microphone read error: {e}")
                        break

                stream.stop_stream()
                stream.close()
                logger.info("Microphone recording stopped")

            except Exception as e:
                logger.error(f"Microphone recording error: {e}")

        self.mic_audio_thread = threading.Thread(target=record_mic)
        self.mic_audio_thread.start()

    def stop_recording(self):
        """Stop recording and mix audio"""
        if not self.recording:
            logger.warning("No recording in progress")
            return None

        logger.info("Stopping recording...")
        self.recording = False

        if hasattr(self, 'system_audio_thread'):
            self.system_audio_thread.join()
        if hasattr(self, 'mic_audio_thread'):
            self.mic_audio_thread.join()
        if hasattr(self, 'screen_thread'):
            self.screen_thread.join()

        if self.video_writer:
            self.video_writer.release()

        mixed_audio_file = self.mix_audio_sources()

        logger.info("✅ Recording stopped successfully")
        return mixed_audio_file

    def mix_audio_sources(self):
        """Mix system audio and microphone into one file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mixed_filename = f"mixed_audio_{timestamp}.wav"

        try:
            system_audio = None
            mic_audio = None

            if self.system_audio_frames:
                logger.info("Processing system audio...")
                with wave.open(f"temp_system_{timestamp}.wav", 'wb') as wf:
                    wf.setnchannels(2)
                    wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(self.audio_sample_rate)
                    wf.writeframes(b''.join(self.system_audio_frames))

                system_audio = AudioSegment.from_wav(f"temp_system_{timestamp}.wav")
                os.remove(f"temp_system_{timestamp}.wav")  # cleanup temp file

            if self.mic_audio_frames:
                logger.info("Processing microphone audio...")
                with wave.open(f"temp_mic_{timestamp}.wav", 'wb') as wf:
                    wf.setnchannels(2)
                    wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(self.audio_sample_rate)
                    wf.writeframes(b''.join(self.mic_audio_frames))

                mic_audio = AudioSegment.from_wav(f"temp_mic_{timestamp}.wav")
                os.remove(f"temp_mic_{timestamp}.wav")  # cleanup temp file

            if system_audio and mic_audio:
                logger.info("Mixing system audio + microphone...")
                min_length = min(len(system_audio), len(mic_audio))
                system_audio = system_audio[:min_length]
                mic_audio = mic_audio[:min_length]
                mixed = system_audio.overlay(mic_audio - 6)  # -6dB for mic to avoid overpowering

            elif system_audio:
                logger.info("Using system audio only...")
                mixed = system_audio

            elif mic_audio:
                logger.info("Using microphone only...")
                mixed = mic_audio

            else:
                logger.warning("No audio recorded!")
                return None

            mixed.export(mixed_filename, format="wav")
            logger.info(f"✅ Mixed audio saved as {mixed_filename}")

            return mixed_filename

        except Exception as e:
            logger.error(f"Error mixing audio: {e}")
            return None

    def transcribe_audio(self, audio_file):
        """Transcribe mixed audio"""
        logger.info(f"Transcribing: {audio_file}")

        try:
            result = self.whisper_model.transcribe(audio_file)
            transcript = result["text"]

            transcript_file = audio_file.replace(".wav", "_transcript.txt")
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(transcript)

            logger.info(f"Transcript saved: {transcript_file}")
            return transcript, transcript_file

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None, None

    def summarize_transcript(self, transcript, model="mistral"):
        """Generate meeting summary"""
        logger.info("Generating meeting summary...")

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

        try:
            response = ollama.chat(model=model, messages=[
                {'role': 'user', 'content': prompt}
            ])

            summary = response['message']['content']

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = f"meeting_summary_{timestamp}.md"

            with open(summary_file, "w", encoding="utf-8") as f:
                f.write(f"# Google Meet Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(summary)

            logger.info(f"Summary saved: {summary_file}")
            return summary, summary_file

        except Exception as e:
            logger.error(f"Summary error: {e}")
            return None, None

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'audio'):
            self.audio.terminate()

def main():
    """Main function"""
    from process_recording import process_recording, get_recording_type_and_name

    print("🎥🎤 Dual Audio Google Meet Recording Bot")
    print("=" * 60)
    print("Records BOTH system audio (others) AND microphone (you)")
    print("=" * 60)

    recording_type, custom_name = get_recording_type_and_name()
    if recording_type is None:
        return

    recorder = DualAudioRecorder()

    print("\nOptions:")
    print("1. Record full meeting (system audio + microphone)")
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
                duration = input("Enter duration in minutes (default 60): ").strip()

                try:
                    duration = int(duration) if duration else 60
                    print(f"\n🎬 Starting DUAL audio recording for {duration} minutes...")
                    print("📺 Screen: Full screen")
                    print("🔊 System audio: Meeting voices")
                    print("🎤 Microphone: Your voice")
                    print("\nPress Ctrl+C to stop early")

                    output_filename = recorder.start_recording()
                    time.sleep(duration * 60)
                    audio_file = recorder.stop_recording()

                    if audio_file:
                        print("\n🔄 Organizing session and processing...")
                        session_dir = process_recording(audio_file, f"{output_filename}.avi", None, recording_type, custom_name)
                        print(f"\n✅ Session processed successfully: {session_dir}")

                except ValueError:
                    print("❌ Invalid duration")
                except KeyboardInterrupt:
                    print("\n⏹️ Stopping recording...")
                    audio_file = recorder.stop_recording()

                    if audio_file:
                        print("🔄 Organizing interrupted session and processing...")
                        session_dir = process_recording(audio_file, f"{output_filename}.avi", None, recording_type, custom_name)
                        print(f"✅ Interrupted session processed successfully: {session_dir}")

            elif choice == "2":
                print("\nTo select a region:")
                print("1. Position your mouse at the top-left corner")
                print("2. Note the coordinates")

                try:
                    x = int(input("Enter X coordinate: "))
                    y = int(input("Enter Y coordinate: "))
                    width = int(input("Enter width: "))
                    height = int(input("Enter height: "))
                    duration = input("Enter duration in minutes (default 60): ").strip()
                    duration = int(duration) if duration else 60

                    region = (x, y, width, height)
                    print(f"\n🎬 Starting region recording for {duration} minutes...")
                    print(f"📺 Region: {region}")
                    print("🔊 System audio + 🎤 Microphone")

                    output_filename = recorder.start_recording(region=region)
                    time.sleep(duration * 60)

                    audio_file = recorder.stop_recording()
                    if audio_file:
                        print("\n🔄 Organizing session and processing...")
                        session_dir = process_recording(audio_file, f"{output_filename}.avi", None, recording_type, custom_name)
                        print("✅ Files organized and processed!")

                except ValueError:
                    print("❌ Invalid input")
                except KeyboardInterrupt:
                    recorder.stop_recording()

            elif choice == "3":
                print("\n🎛️ Manual Control Mode")
                print("Commands: 'start', 'stop', 'quit'")

                output_filename = None
                while True:
                    command = input("\nEnter command: ").strip().lower()

                    if command == 'start':
                        if not recorder.recording:
                            output_filename = recorder.start_recording()
                            print("✅ DUAL recording started!")
                            print("🔊 System audio + 🎤 Microphone")
                        else:
                            print("⚠️ Already recording!")

                    elif command == 'stop':
                        if recorder.recording:
                            audio_file = recorder.stop_recording()
                            if audio_file:
                                print("🔄 Organizing session and processing...")
                                session_dir = process_recording(audio_file, f"{output_filename}.avi", None, recording_type, custom_name)
                                print("✅ Files organized and processed!")
                        else:
                            print("⚠️ Not recording!")

                    elif command == 'quit':
                        if recorder.recording:
                            recorder.stop_recording()
                        break

                    else:
                        print("❌ Unknown command. Use 'start', 'stop', or 'quit'")
            else:
                print("❌ Invalid option. Please select 0-3.")

    finally:
        recorder.cleanup()

if __name__ == "__main__":
    main()
