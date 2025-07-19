#!/usr/bin/env python3
"""
Setup script for Google Meet Bot
This script installs all required dependencies and sets up Ollama
"""

import subprocess
import sys
import os
import requests
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        if platform.system() == "Windows":
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def install_python_packages():
    """Install required Python packages"""
    print("Installing Python packages...")

    success = run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

    if not success:
        packages = [
            "sounddevice==0.4.6",
            "pydub==0.25.1",
            "openai-whisper==20231117",
            "torch==2.1.0",
            "transformers==4.35.0",
            "selenium==4.15.0",
            "opencv-python==4.8.1.78",
            "requests==2.31.0",
            "numpy==1.24.3",
            "webdriver-manager==4.0.1",
            "ollama==0.1.7"
        ]

        for package in packages:
            run_command(
                f"{sys.executable} -m pip install {package}",
                f"Installing {package}"
            )

def install_ollama():
    """Install Ollama based on the operating system"""
    system = platform.system()

    print(f"\nInstalling Ollama for {system}...")

    if system == "Windows":
        print("Please download and install Ollama manually:")
        print("1. Go to: https://ollama.ai/download")
        print("2. Download the Windows installer")
        print("3. Run the installer")
        print("4. After installation, restart your terminal")
        print("5. Run: ollama pull mistral")

    elif system == "Darwin":  # macOS
        success = run_command(
            "curl -fsSL https://ollama.ai/install.sh | sh",
            "Installing Ollama on macOS"
        )
        if success:
            run_command("ollama pull mistral", "Pulling Mistral model")

    elif system == "Linux":
        success = run_command(
            "curl -fsSL https://ollama.ai/install.sh | sh",
            "Installing Ollama on Linux"
        )
        if success:
            run_command("ollama pull mistral", "Pulling Mistral model")

    else:
        print(f"❌ Unsupported operating system: {system}")

def check_ffmpeg():
    """Check if FFmpeg is installed (required for pydub)"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ FFmpeg is already installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found")

        system = platform.system()
        if system == "Windows":
            print("Please install FFmpeg:")
            print("1. Download from: https://ffmpeg.org/download.html")
            print("2. Extract to a folder (e.g., C:\\ffmpeg)")
            print("3. Add C:\\ffmpeg\\bin to your PATH environment variable")
        elif system == "Darwin":
            print("Install FFmpeg with: brew install ffmpeg")
        elif system == "Linux":
            print("Install FFmpeg with: sudo apt install ffmpeg")

        return False

def setup_audio_permissions():
    """Guide user through audio permission setup"""
    system = platform.system()

    print(f"\n🎤 Audio Permission Setup for {system}:")

    if system == "Windows":
        print("1. Right-click on the speaker icon in the system tray")
        print("2. Select 'Open Sound settings'")
        print("3. Scroll down to 'Advanced sound options'")
        print("4. Click 'App volume and device preferences'")
        print("5. Enable 'Stereo Mix' in Recording devices if available")
        print("6. If Stereo Mix is not available:")
        print("   - Right-click in Recording devices area")
        print("   - Select 'Show Disabled Devices' and 'Show Disconnected Devices'")
        print("   - Right-click 'Stereo Mix' and select 'Enable'")

    elif system == "Darwin":
        print("1. Go to System Preferences > Security & Privacy > Privacy")
        print("2. Select 'Microphone' from the left sidebar")
        print("3. Check the box next to Terminal or your Python IDE")
        print("4. You might need to install additional software like:")
        print("   - Soundflower: https://github.com/mattingalls/Soundflower")
        print("   - BlackHole: https://github.com/ExistentialAudio/BlackHole")

    elif system == "Linux":
        print("1. Install PulseAudio if not already installed")
        print("2. Use pavucontrol for audio device management")
        print("3. You might need to configure audio loopback:")
        print("   sudo modprobe snd-aloop")

def create_test_script():
    """Create a simple test script"""
    test_script = '''#!/usr/bin/env python3
"""
Test script for Google Meet Bot components
"""

import sys

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...")

    try:
        import sounddevice as sd
        print("✅ sounddevice imported successfully")
    except ImportError as e:
        print(f"❌ sounddevice import failed: {e}")

    try:
        import whisper
        print("✅ whisper imported successfully")
    except ImportError as e:
        print(f"❌ whisper import failed: {e}")

    try:
        import ollama
        print("✅ ollama imported successfully")
    except ImportError as e:
        print(f"❌ ollama import failed: {e}")

    try:
        from selenium import webdriver
        print("✅ selenium imported successfully")
    except ImportError as e:
        print(f"❌ selenium import failed: {e}")

    try:
        import cv2
        print("✅ opencv-python imported successfully")
    except ImportError as e:
        print(f"❌ opencv-python import failed: {e}")

def test_ollama():
    """Test Ollama connection"""
    print("\\nTesting Ollama connection...")
    try:
        import ollama
        models = ollama.list()
        print(f"✅ Ollama is running. Available models: {len(models['models'])}")

        model_names = [model['name'] for model in models['models']]
        if any('mistral' in name.lower() for name in model_names):
            print("✅ Mistral model is available")
        else:
            print("❌ Mistral model not found. Run: ollama pull mistral")

    except Exception as e:
        print(f"❌ Ollama test failed: {e}")

def test_audio_devices():
    """Test audio device detection"""
    print("\\nTesting audio devices...")
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        print(f"✅ Found {len(devices)} audio devices")

        # List input devices
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        print(f"✅ Found {len(input_devices)} input devices")

    except Exception as e:
        print(f"❌ Audio device test failed: {e}")

if __name__ == "__main__":
    print("Google Meet Bot - Component Test")
    print("=" * 40)

    test_imports()
    test_ollama()
    test_audio_devices()

    print("\\n" + "=" * 40)
    print("Test completed!")
'''

    with open("test_setup.py", "w") as f:
        f.write(test_script)

    print("✅ Created test_setup.py")

def main():
    """Main setup function"""
    print("Google Meet Bot Setup")
    print("=" * 40)

    install_python_packages()
    check_ffmpeg()
    install_ollama()
    setup_audio_permissions()
    create_test_script()

    print("\n" + "=" * 40)
    print("Setup completed!")
    print("\nNext steps:")
    print("1. Run 'python test_setup.py' to verify installation")
    print("2. If on Windows, ensure Ollama is installed manually")
    print("3. Run 'ollama pull mistral' if not done automatically")
    print("4. Test audio recording with 'python system_audio_recorder.py'")
    print("5. Run the main bot with 'python meet_bot.py'")

if __name__ == "__main__":
    main()
