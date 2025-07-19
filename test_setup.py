#!/usr/bin/env python3
"""
Test script for Google Meet Bot components
"""

import sys

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...")

    try:
        import sounddevice as sd
        print("+ sounddevice imported successfully")
    except ImportError as e:
        print(f"- sounddevice import failed: {e}")

    try:
        import whisper
        print("+ whisper imported successfully")
    except ImportError as e:
        print(f"- whisper import failed: {e}")

    try:
        import ollama
        print("+ ollama imported successfully")
    except ImportError as e:
        print(f"- ollama import failed: {e}")

    try:
        from selenium import webdriver
        print("+ selenium imported successfully")
    except ImportError as e:
        print(f"- selenium import failed: {e}")

    try:
        import cv2
        print("+ opencv-python imported successfully")
    except ImportError as e:
        print(f"- opencv-python import failed: {e}")

def test_ollama():
    """Test Ollama connection"""
    print("\nTesting Ollama connection...")
    try:
        import ollama
        models = ollama.list()
        print(f"+ Ollama is running. Available models: {len(models['models'])}")

        model_names = [model.model for model in models['models']]
        print(f"+ Model names: {model_names}")

        if any('mistral' in name.lower() for name in model_names):
            print("+ Mistral model is available")
        else:
            print("- Mistral model not found. Run: ollama pull mistral")

    except Exception as e:
        print(f"- Ollama test failed: {e}")

def test_audio_devices():
    """Test audio device detection"""
    print("\nTesting audio devices...")
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        print(f"+ Found {len(devices)} audio devices")

        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        print(f"+ Found {len(input_devices)} input devices")

    except Exception as e:
        print(f"- Audio device test failed: {e}")

if __name__ == "__main__":
    print("Google Meet Bot - Component Test")
    print("=" * 40)

    test_imports()
    test_ollama()
    test_audio_devices()

    print("\n" + "=" * 40)
    print("Test completed!")
