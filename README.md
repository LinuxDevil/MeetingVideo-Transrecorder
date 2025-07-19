# Dual Audio Recording Bot

An Python bot that records dual audio (system + microphone) with screen capture, automatically transcribes using OpenAI Whisper, and generates AI-powered summaries using Ollama. Perfect for lessons, meetings, and video recordings with comprehensive session management.

## Features

- 🎥 **Dual audio + screen recording** (system audio + microphone + video)
- 📁 **Smart session organization** - automatically creates timestamped directories
- 🎯 **Flexible recording types** - Google Meet, Lesson, or general Video recording
- 🎤 **Enhanced audio processing** - video audio extraction with mixed audio fallback
- 📝 **Advanced transcription** with OpenAI Whisper (offline)
- 📋 **AI-powered summaries** using Ollama tailored by recording type
- 🔒 **100% open-source** - no paid APIs required
- 💻 **Cross-platform support** (Windows, macOS, Linux)
- 🛠️ **Command-line and interactive modes** for maximum flexibility

## Demo Video

[![Demo Video](assets/result.mp4)](assets/result.mp4)

*Click to view a demonstration of the dual audio recording bot in action, showing screen recording, audio capture, transcription, and AI summarization.*

## Prerequisites

### System Requirements

- Python 3.8 or higher
- Chrome browser installed
- At least 4GB RAM (for Whisper model)
- Audio drivers that support system audio recording

### Required Software

1. **Python 3.8+**
2. **Chrome Browser**
3. **FFmpeg** (for audio processing)
4. **Ollama** (for AI summarization)

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone or download the project files
# Navigate to the project directory
cd google-meet-bot

# Run the automated setup
python setup.py
```

### Option 2: Manual Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install FFmpeg:**
   - **Windows**: Download from [FFmpeg.org](https://ffmpeg.org/download.html)
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

3. **Install Ollama:**
   - **Windows**: Download from [Ollama.ai](https://ollama.ai/download)
   - **macOS/Linux**: `curl -fsSL https://ollama.ai/install.sh | sh`

4. **Download AI model:**
```bash
ollama pull mistral
```

## Configuration

### Audio Setup (Critical!)

The bot needs to capture system audio to record the meeting participants. This requires specific audio configuration:

#### Windows
1. Right-click speaker icon → "Open Sound settings"
2. Scroll to "Advanced sound options" → "App volume and device preferences"
3. Enable "Stereo Mix" in Recording devices:
   - Right-click in Recording area
   - Check "Show Disabled Devices" and "Show Disconnected Devices"
   - Right-click "Stereo Mix" → "Enable"

#### Windows 11
 To enable Stereo Mix on Windows 11, right-click the speaker icon in the system tray and select "Open sound settings". Navigate to "More sound settings" and then the "Recording" tab. If Stereo Mix is not visible, right-click and select "Show disabled devices" and "Show disconnected devices". Right-click on Stereo Mix and select "Enable". If it still doesn't appear, your sound card or drivers might need updating.

#### macOS
1. Install additional audio software:
   - [BlackHole](https://github.com/ExistentialAudio/BlackHole) (recommended)
   - [Soundflower](https://github.com/mattingalls/Soundflower)
2. System Preferences → Security & Privacy → Privacy → Microphone
3. Enable access for Terminal/Python

#### Linux
```bash
# Install PulseAudio tools
sudo apt install pavucontrol

# Enable audio loopback
sudo modprobe snd-aloop
```

## Usage

### Quick Start

1. **Test your setup:**
```bash
python test_setup.py
```

2. **Run the enhanced dual audio bot:**
```bash
python dual_audio_bot.py
```

3. **Process existing recordings (optional):**
```bash
python process_recording.py
```

### Recording Types

The bot supports three recording types with tailored AI summaries:

#### 1. Google Meet 🎥
Optimized for meeting recordings with focus on:
- Decisions made and action items
- Key discussion points
- Participant contributions
- Follow-up tasks

#### 2. Lesson 📚
Perfect for educational content with emphasis on:
- Learning objectives and key concepts
- Important explanations and examples
- Questions and answers
- Practical applications

#### 3. Video 🎬
General purpose recording for:
- Tutorials and demonstrations
- Presentations and webinars
- Any other video content

### Recording Options

#### 1. Full Screen Recording (Recommended)
- Records entire screen with dual audio
- Perfect for meetings and lessons
- Automatic duration or manual stop

#### 2. Screen Region Recording
- Select specific area to record
- Reduces file size
- Good for focused content

#### 3. Manual Control
- Start/stop recording manually
- Maximum flexibility
- Interactive control during recording

## Session Organization

The bot automatically organizes each recording into a timestamped session directory:

```
sessions/
└── Lesson_MyTopic_20250120_143000/
    ├── audio.wav              # Mixed system + microphone audio
    ├── video.avi              # Screen recording
    ├── transcript.txt         # Full transcription
    ├── summary.txt            # AI-generated summary
    └── session_info.json      # Session metadata
```

### File Details

- **`audio.wav`** - High-quality mixed audio (system + microphone)
- **`video.avi`** - Screen recording with optimized compression
- **`transcript.txt`** - Complete transcription from video or mixed audio
- **`summary.txt`** - AI-powered summary tailored to recording type
- **`session_info.json`** - Metadata including transcript source and processing details

### Directory Naming Convention

- **Google Meet**: `GoogleMeet_[CustomName]_YYYYMMDD_HHMMSS`
- **Lesson**: `Lesson_[LessonName]_YYYYMMDD_HHMMSS`
- **Video**: `Video_[CustomName]_YYYYMMDD_HHMMSS`

### Enhanced Audio Processing

The system uses a smart audio selection approach:
1. **First**: Attempts to extract audio directly from video (most accurate)
2. **Fallback**: Uses mixed audio if video has no audio stream
3. **Metadata**: Records which audio source was used for transparency

### Sample Summary Formats

#### Google Meet Summary
```
# Meeting Summary

## Key Decisions
- Project deadline extended to March 15th
- Budget approved for additional developer hire

## Action Items
- John: Technical specification by Friday
- Sarah: Budget review by next Tuesday

## Important Discussions
- Client feedback integration strategy
- Security audit timeline and requirements
```

#### Lesson Summary
```
# Lesson: React Development Patterns

## Key Concepts
- Component composition vs inheritance
- State management patterns
- Performance optimization techniques

## Learning Objectives Covered
- Understanding React's component lifecycle
- Implementing custom hooks effectively
- Best practices for state management

## Practical Examples
- Building a todo app with useState
- Creating reusable form components
```

## Troubleshooting

### Common Issues

#### 1. Audio Recording Problems
```bash
# Test available audio devices during bot startup
python dual_audio_bot.py

# The bot will show detected audio devices
# If no system audio device found:
# - Check Windows Stereo Mix is enabled
# - Install additional audio software on macOS
# - Configure PulseAudio on Linux
```

#### 2. FFmpeg Issues
```bash
# Test FFmpeg installation
ffmpeg -version

# If not found, reinstall:
# Windows: Download from FFmpeg.org
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

#### 3. Whisper Model Loading Issues
```bash
# Clear Whisper cache and reinstall
pip uninstall openai-whisper
pip install openai-whisper==20231117
```

#### 4. Ollama Connection Problems
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Pull required model
ollama pull mistral
```

### Audio Permissions

If you get permission errors:

1. **Windows**: Run as Administrator initially
2. **macOS**: Grant microphone access to Terminal
3. **Linux**: Add user to audio group:
```bash
sudo usermod -a -G audio $USER
```

## Customization

### Using Different AI Models

Replace `mistral` with other Ollama models in `process_recording.py`:

```python
# Edit line in generate_summary() function
# Available models: llama2, codellama, vicuna, phi, etc.
response = ollama.chat(
    model='llama2',  # Change this to your preferred model
    messages=messages
)
```

### Command Line Processing

Process existing recordings with custom parameters:

```bash
# Process specific files
python process_recording.py --audio mixed_audio.wav --video recording.avi

# Specify recording type and custom name
python process_recording.py --type lesson --name "Advanced Python"

# Process without prompts (use default values)
python process_recording.py --audio audio.wav --video video.avi --type meeting --name "Team Sync" --no-prompts
```

### Custom Summarization Prompts

Modify the prompts in `process_recording.py` for different recording types:

```python
# For Google Meet recordings
meet_prompt = """
Analyze this meeting transcript and provide:
1. Key decisions made
2. Action items with assignees
3. Important discussion points
4. Follow-up tasks
"""

# For Lesson recordings
lesson_prompt = """
Analyze this lesson transcript and provide:
1. Main learning objectives covered
2. Key concepts explained
3. Practical examples demonstrated
4. Questions and answers
"""
```

## Security & Privacy

- ✅ **All processing is local** - no data sent to external services
- ✅ **Open-source models** - Whisper and Ollama models run offline
- ✅ **No API keys required** - completely self-contained
- ✅ **Session organization** - automatic cleanup and structured storage
- ⚠️ **Audio files stored locally** - ensure proper file permissions
- ⚠️ **Screen recording** - captures all visible content during recording

## Performance Considerations

- **RAM Usage**: Whisper models require 1-4GB RAM
- **Processing Time**: ~1-2 minutes per hour of audio for transcription
- **Storage**: ~50MB per hour for dual audio + video (compressed)
- **CPU**: Transcription and video processing are CPU-intensive
- **FFmpeg dependency**: Required for video audio extraction

## Legal Considerations

⚠️ **Important**: Always comply with local laws and meeting policies:

- Get consent from all participants before recording
- Check your organization's recording policies
- Respect privacy laws (GDPR, CCPA, etc.)
- Only record meetings you're authorized to record

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Run `python test_setup.py` to verify installation
3. Test components individually before running full sessions

## Roadmap

### Completed ✅
- ✅ **Dual audio recording** (system + microphone)
- ✅ **Screen recording** with video capture
- ✅ **Smart session organization** with timestamped directories
- ✅ **Enhanced audio processing** with video audio extraction
- ✅ **Flexible recording types** (Google Meet, Lesson, Video)
- ✅ **AI-powered summaries** tailored by content type
- ✅ **Command-line interface** for batch processing

### Planned Features 🚀
- [ ] **Real-time transcription** display during recording
- [ ] **Multiple language support** for transcription
- [ ] **Speaker identification** and diarization
- [ ] **Microsoft Teams integration**
- [ ] **Calendar integration** for automatic recording
- [ ] **Email summaries** with automatic distribution
- [ ] **Web interface** for remote control
- [ ] **Mobile companion app** for notifications
- [ ] **Cloud sync** options (optional)
- [ ] **Advanced video editing** with chapter markers
