# Android Voice Assistant (Termux + Claude)

An open-source voice assistant for Android that runs in Termux and uses Claude for intelligent responses.

## Features

- **Voice & Text Input**: Switch between voice commands and text input
- **SMS**: Read and send text messages
- **Notes**: Take, read, list, and delete notes (stored locally)
- **Clipboard**: Read and write to clipboard
- **Notifications**: Display system notifications
- **Battery**: Check battery status
- **Contacts**: Search contacts by name
- **Claude-Powered**: Natural language understanding with tool use

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Android Phone                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                      Termux                              ││
│  │                                                          ││
│  │   Voice/Text  ──→  Claude API  ──→  Tool Execution      ││
│  │       │               │                  │               ││
│  │       │               │                  ▼               ││
│  │       │               │         termux-api commands      ││
│  │       │               │         (sms, tts, etc.)         ││
│  │       ▼               ▼                  │               ││
│  │   Response  ←──  AI Response  ←─────────┘               ││
│  │                                                          ││
│  └─────────────────────────────────────────────────────────┘│
│  ┌─────────────────┐                                        │
│  │   Termux:API    │  ← Android system integration          │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Apps (Install ALL from F-Droid)

> **Important**: Do NOT mix F-Droid and Play Store versions!

1. [F-Droid](https://f-droid.org/) - Open source app store
2. [Termux](https://f-droid.org/en/packages/com.termux/) - Terminal emulator
3. [Termux:API](https://f-droid.org/en/packages/com.termux.api/) - Android API access
4. [Termux:Boot](https://f-droid.org/en/packages/com.termux.boot/) - Auto-start (optional)

### API Key

You need an Anthropic API key from [console.anthropic.com](https://console.anthropic.com/)

## Installation

### 1. Clone the repository

In Termux:
```bash
pkg install git
git clone https://github.com/YOUR_USERNAME/andrassistant.git
cd andrassistant
```

### 2. Run the setup script

```bash
chmod +x setup_termux.sh
./setup_termux.sh
```

### 3. Set your API key

```bash
export ANTHROPIC_API_KEY='sk-ant-your-key-here'
echo 'export ANTHROPIC_API_KEY="sk-ant-your-key-here"' >> ~/.bashrc
```

### 4. Grant Android permissions

Go to **Android Settings → Apps → Termux:API → Permissions** and enable:
- Microphone (for voice input)
- SMS (for reading/sending messages)
- Contacts (for contact lookup)
- Notifications (for showing notifications)

### 5. Restart Termux

```bash
source ~/.bashrc
```

## Usage

### Text Mode (default, for testing)
```bash
assistant
# or
python assistant.py --text
```

### Voice Mode
```bash
assistant-voice
# or
python assistant.py --voice
```

### Example Commands

**SMS:**
- "Read my messages"
- "Read messages from Mom"
- "Send a text to +1234567890 saying I'll be there in 10 minutes"
- "Text John that I'm running late"

**Notes:**
- "Take a note: remember to buy milk and eggs"
- "What notes do I have?"
- "Read my notes"
- "Delete the note from today"

**Other:**
- "What's my battery level?"
- "Copy this to clipboard: hello world"
- "What's in my clipboard?"
- "Find contact John"

## File Structure

```
andrassistant/
├── assistant.py        # Main assistant script
├── requirements.txt    # Python dependencies
├── setup_termux.sh     # Termux setup script
├── README.md           # This file
└── .gitignore

~/notes/                # Notes storage (created automatically)
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (required) |

### Changing the AI Model

Edit `assistant.py` and change the model in the `chat()` function:
```python
model="claude-sonnet-4-20250514"  # or claude-haiku-4-20250514 for faster/cheaper
```

## Troubleshooting

### "termux-speech-to-text" doesn't work

The default STT uses Google's speech recognition. Make sure:
1. Google app is installed and enabled
2. You have internet connection
3. Microphone permission is granted

For offline STT, see the "Offline Speech Recognition" section below.

### Commands timeout or fail

- Check that Termux:API app is installed from F-Droid
- Check permissions in Android settings
- Run `termux-sms-list` directly to test

### Battery drain

- Disable battery optimization: Settings → Apps → Termux → Battery → Unrestricted
- Use text mode when testing
- Consider using wake word + dedicated hardware for always-on

### Android 12+ kills Termux

Android 12+ aggressively kills background processes. Solutions:
1. Disable battery optimization
2. Run `termux-wake-lock` before starting
3. Keep Termux in foreground or use a persistent notification

## Optional: Offline Speech Recognition

To avoid using Google STT, you can set up Vosk:

```bash
pkg install python
pip install vosk sounddevice

# Download a model (~50MB for small English)
mkdir -p ~/models && cd ~/models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

Then modify the `listen()` function in `assistant.py` to use Vosk.

## Optional: Wake Word Detection

For "Hey Assistant" style activation, integrate with:
- [wyoming-satellite-termux](https://github.com/pantherale0/wyoming-satellite-termux)
- [Porcupine](https://picovoice.ai/platform/porcupine/) (requires custom integration)

## Termux:API Command Reference

Commands used by this assistant:

| Command | Description |
|---------|-------------|
| `termux-speech-to-text` | Voice input (uses Google) |
| `termux-tts-speak TEXT` | Text to speech |
| `termux-sms-list` | List SMS messages |
| `termux-sms-send -n NUM MSG` | Send SMS |
| `termux-contact-list` | List all contacts |
| `termux-clipboard-get` | Read clipboard |
| `termux-clipboard-set TEXT` | Write clipboard |
| `termux-notification` | Show notification |
| `termux-battery-status` | Battery info |
| `termux-vibrate` | Vibrate phone |
| `termux-toast MSG` | Show toast |

Full list: [Termux:API Wiki](https://wiki.termux.com/wiki/Termux:API)

## License

MIT License - feel free to modify and distribute.

## Contributing

Contributions welcome! Ideas for improvement:
- Offline STT integration (Vosk/Whisper)
- Wake word detection
- Calendar integration
- Email support
- WhatsApp/Telegram via Tasker integration
- Local LLM support (Ollama)
