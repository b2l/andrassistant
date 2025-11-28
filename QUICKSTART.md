# Quick Start - Minimal Test (No Claude)

Test that Termux:API works before adding Claude integration.

## 1. Install Apps (F-Droid only!)

From [F-Droid](https://f-droid.org/):
- **Termux** - Terminal emulator
- **Termux:API** - Android API access

> ⚠️ Do NOT install from Play Store - versions are incompatible!

## 2. Setup Termux

Open Termux and run:

```bash
# Update packages
pkg update && pkg upgrade

# Install termux-api package
pkg install termux-api

# Setup storage access
termux-setup-storage
```

## 3. Grant Permissions

Go to **Android Settings → Apps → Termux:API → Permissions**

Enable:
- ✅ Microphone
- ✅ SMS
- ✅ Contacts (optional)
- ✅ Notifications (optional)

## 4. Test Individual Commands

```bash
# Test TTS (should speak)
termux-tts-speak "Hello world"

# Test battery
termux-battery-status

# Test clipboard
termux-clipboard-set "test"
termux-clipboard-get

# Test SMS (needs permission)
termux-sms-list -l 1

# Test voice input (needs Google app + microphone)
termux-speech-to-text
```

## 5. Run Minimal Assistant

```bash
# Get the script (adjust path as needed)
# Option A: Clone repo
pkg install git
git clone <your-repo-url>
cd andrassistant

# Option B: Just download the script
curl -O https://raw.githubusercontent.com/<user>/andrassistant/main/minimal_test.sh

# Run it
chmod +x minimal_test.sh
./minimal_test.sh
```

## 6. Available Commands (Minimal Version)

| Say | Does |
|-----|------|
| "What's my battery?" | Reads battery level |
| "What time is it?" | Reads current time |
| "What's the date?" | Reads current date |
| "Read my messages" | Reads last SMS |
| "What's in my clipboard?" | Reads clipboard |
| "Note remember to buy milk" | Saves a note |
| "Help" | Lists commands |
| "Quit" | Exits |

## Troubleshooting

### Voice input doesn't work
- Make sure Google app is installed and enabled
- Check microphone permission for Termux:API
- Try: `termux-speech-to-text` directly

### SMS doesn't work
- Grant SMS permission to Termux:API app
- Test: `termux-sms-list -l 1`

### TTS doesn't work
- Check that a TTS engine is installed (Google TTS usually pre-installed)
- Test: `termux-tts-speak "test"`

### Commands fail silently
- Run `termux-battery-status` to test basic API
- If nothing works, reinstall Termux:API from F-Droid

## Next Steps

Once this works, you can set up the full Claude-powered assistant:

```bash
pkg install python
pip install anthropic
export ANTHROPIC_API_KEY='sk-ant-xxx'
python assistant.py
```
