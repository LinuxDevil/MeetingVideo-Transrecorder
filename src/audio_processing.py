"""
Audio processing for dual audio recording
"""

import pyaudio
import wave
from pydub import AudioSegment
import os
import threading
from datetime import datetime
from typing import Optional
from src.config import config
from src.utils import setup_logging

logger = setup_logging(level=config.log_level)

class AudioRecorder:
    """
    Dual audio recorder implementation
    """
    def __init__(self):
        self.audio_interface = pyaudio.PyAudio()
        self.system_audio_frames = []
        self.mic_audio_frames = []
        self.recording = False
        self.system_audio_device = None
        self.mic_device = None
        self.system_device_info = None
        self.mic_device_info = None

    def find_audio_devices(self):
        """Find and set input devices for system audio and microphone"""
        logger.info("Scanning for audio devices...")
        system_keywords = ['stereo mix', 'what you hear', 'wave out mix', 'loopback', 'monitor']
        mic_keywords = ['microphone', 'mic', 'hyperx', 'webcam', 'camera', 'headset', 'array']
        system_candidates = []
        mic_candidates = []

        try:
            for i in range(self.audio_interface.get_device_count()):
                device_info = self.audio_interface.get_device_info_by_index(i)
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
            if self.mic_device is None:
                logger.warning("⚠️ No microphone found!")

        except Exception as e:
            logger.error(f"Error scanning devices: {e}")

    def start_recording(self):
        """Start recording audio from system and microphone"""
        self.recording = True
        self.system_audio_frames = []
        self.mic_audio_frames = []

        self.system_audio_thread = threading.Thread(target=self.record_system_audio)
        self.mic_audio_thread = threading.Thread(target=self.record_microphone)

        logger.info("Starting audio recording...")
        self.system_audio_thread.start()
        self.mic_audio_thread.start()

    def record_system_audio(self):
        """Record system audio (what you hear)"""
        if self.system_audio_device is None:
            logger.warning("No system audio device - skipping")
            return

        try:
            format = pyaudio.paInt16
            channels = min(config.audio.channels, self.system_device_info['maxInputChannels'])

            stream = self.audio_interface.open(
                format=format,
                channels=channels,
                rate=config.audio.sample_rate,
                input=True,
                input_device_index=self.system_audio_device,
                frames_per_buffer=config.audio.chunk_size
            )

            logger.info(f"Recording system audio: {channels} channels")

            while self.recording:
                try:
                    data = stream.read(config.audio.chunk_size, exception_on_overflow=False)
                    self.system_audio_frames.append(data)
                except Exception as e:
                    logger.error(f"System audio read error: {e}")
                    break

            stream.stop_stream()
            stream.close()
            logger.info("System audio recording stopped")

        except Exception as e:
            logger.error(f"System audio recording error: {e}")

    def record_microphone(self):
        """Record microphone (your voice)"""
        if self.mic_device is None:
            logger.warning("No microphone device - skipping")
            return

        try:
            format = pyaudio.paInt16
            channels = min(config.audio.channels, self.mic_device_info['maxInputChannels'])

            stream = self.audio_interface.open(
                format=format,
                channels=channels,
                rate=config.audio.sample_rate,
                input=True,
                input_device_index=self.mic_device,
                frames_per_buffer=config.audio.chunk_size
            )

            logger.info(f"Recording microphone: {channels} channels")

            while self.recording:
                try:
                    data = stream.read(config.audio.chunk_size, exception_on_overflow=False)
                    self.mic_audio_frames.append(data)
                except Exception as e:
                    logger.error(f"Microphone read error: {e}")
                    break

            stream.stop_stream()
            stream.close()
            logger.info("Microphone recording stopped")

        except Exception as e:
            logger.error(f"Microphone recording error: {e}")

    def stop_recording(self) -> Optional[str]:
        """Stop recording and mix audio sources"""
        if not self.recording:
            logger.warning("No recording in progress")
            return None

        logger.info("Stopping audio recording...")
        self.recording = False

        self.system_audio_thread.join()
        self.mic_audio_thread.join()

        return self.mix_audio_sources()

    def mix_audio_sources(self) -> Optional[str]:
        """Mix system audio and microphone into a single WAV file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mixed_filename = f"mixed_audio_{timestamp}.wav"

        try:
            system_audio = None
            mic_audio = None

            if self.system_audio_frames:
                logger.info("Processing system audio...")
                with wave.open(f"temp_system_{timestamp}.wav", 'wb') as wf:
                    wf.setnchannels(config.audio.channels)
                    wf.setsampwidth(self.audio_interface.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(config.audio.sample_rate)
                    wf.writeframes(b''.join(self.system_audio_frames))

                system_audio = AudioSegment.from_wav(f"temp_system_{timestamp}.wav")
                os.remove(f"temp_system_{timestamp}.wav")

            if self.mic_audio_frames:
                logger.info("Processing microphone audio...")
                with wave.open(f"temp_mic_{timestamp}.wav", 'wb') as wf:
                    wf.setnchannels(config.audio.channels)
                    wf.setsampwidth(self.audio_interface.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(config.audio.sample_rate)
                    wf.writeframes(b''.join(self.mic_audio_frames))

                mic_audio = AudioSegment.from_wav(f"temp_mic_{timestamp}.wav")
                os.remove(f"temp_mic_{timestamp}.wav")

            if system_audio and mic_audio:
                logger.info("Mixing system audio + microphone...")
                min_length = min(len(system_audio), len(mic_audio))
                system_audio = system_audio[:min_length]
                mic_audio = mic_audio[:min_length]
                mixed = system_audio.overlay(mic_audio - config.audio.microphone_reduction_db)

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

    def cleanup(self):
        """Clean up resources"""
        self.audio_interface.terminate()

if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.find_audio_devices()
    recorder.start_recording()
    try:
        import time
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        audio_file = recorder.stop_recording()
        if audio_file:
            logger.info(f"Recorded audio saved: {audio_file}")
        recorder.cleanup()
