# Voice Assistant Research Summary

This document summarizes research conducted on open-source voice assistants for Android, with a focus on hands-free note-taking, SMS, and Claude integration.

## Goal

Build an open-source voice assistant for Android that can:
- Activate by wake word ("Hey Assistant...")
- Take notes hands-free (e.g., while driving, cooking)
- Read/write SMS messages
- Prepare emails
- Use Claude API for intelligent responses
- Run self-hosted/locally where possible

## Options Evaluated

### 1. Home Assistant + Assist (Best Claude Integration)

**What it is:** Self-hosted home automation platform with voice assistant capabilities.

**Pros:**
- Official Anthropic/Claude integration since v2024.9
- Full voice pipeline: wake word → STT → LLM → TTS
- Local STT (Whisper) and TTS (Piper) available
- Android companion app
- Active development, large community

**Cons:**
- Android app does NOT have wake word (need gesture/tap)
- Primarily designed for home automation, not phone control
- Can't directly access phone SMS (only notifications)

**Voice Pipeline Components:**
| Component | Local Option | Cloud Option |
|-----------|--------------|--------------|
| Wake Word | openWakeWord, microWakeWord | - |
| STT | Whisper, Speech-to-Phrase | HA Cloud |
| Conversation | Home Assistant intents | Claude, OpenAI |
| TTS | Piper | HA Cloud |

**Links:**
- https://www.home-assistant.io/integrations/anthropic
- https://www.home-assistant.io/voice_control/
- https://www.home-assistant.io/voice_control/android/

---

### 2. Rhasspy + Rhasspy Mobile

**What it is:** Offline voice assistant toolkit with Android satellite app.

**Pros:**
- Fully offline capable
- Wake word via Porcupine (local)
- Android app available (Rhasspy Mobile)
- Highly customizable intents
- MQTT/HTTP API for integration

**Cons:**
- No native LLM integration (would need custom work)
- Primarily for home automation
- Setup complexity

**Links:**
- https://rhasspy.readthedocs.io/
- https://github.com/Nailik/rhasspy_mobile

---

### 3. OpenVoiceOS / Neon AI (Mycroft Successors)

**What it is:** Community fork of Mycroft (which was archived in 2024).

**Pros:**
- Full voice assistant with skills system
- LLM "Persona" system supports OpenAI-compatible APIs
- 25+ languages
- Privacy-focused

**Cons:**
- Claude not natively supported (would need LiteLLM proxy)
- Complex setup
- Android support via Docker, not native app

**Links:**
- https://github.com/OpenVoiceOS
- https://neon.ai/
- https://pypi.org/project/ovos-persona/

---

### 4. Dicio (Android Native)

**What it is:** Open-source Android voice assistant.

**Pros:**
- Native Android app
- Offline STT via Vosk
- Available on F-Droid
- Simple, lightweight

**Cons:**
- No wake word detection
- No LLM integration
- Limited skills/capabilities

**Links:**
- https://f-droid.org/packages/org.stypox.dicio/
- https://github.com/Stypox/dicio-android

---

### 5. Saiy (Open Source, Feature-Rich)

**What it is:** Open-source Android voice assistant with many integrations.

**Pros:**
- Wake word support
- SMS read/send, calls, calendar, email
- Works offline for basic commands
- Tasker integration
- Open source (AGPL v3)

**Cons:**
- Last major update was years ago
- Depends on Google Play Services for some features
- No LLM integration (rule-based)

**Links:**
- https://github.com/brandall76/Saiy-PS
- https://www.xda-developers.com/saiy-offline-voice-assistant-open-source/

---

### 6. Tasker + AutoVoice (Most Practical, Not OSS)

**What it is:** Android automation app with voice plugin.

**Pros:**
- Wake word via AutoVoice
- Full phone access (SMS, notifications, apps)
- Can integrate with any API (Claude, etc.)
- Very flexible

**Cons:**
- Not open source
- Paid apps (~$3-10 total)
- Requires significant setup

---

### 7. Termux + Claude API (Chosen Approach)

**What it is:** Linux terminal on Android with Python and system APIs.

**Pros:**
- Fully open source
- Direct phone access via Termux:API (SMS, contacts, clipboard, TTS)
- Can use Claude API with tool calling
- Full control, hackable
- Can add wake word via Wyoming or Porcupine

**Cons:**
- DIY effort required
- `termux-speech-to-text` uses Google (not fully open)
- Battery usage if always-on
- No native wake word (needs workaround)

**Termux:API Commands:**
```bash
termux-sms-list          # Read SMS
termux-sms-send          # Send SMS
termux-speech-to-text    # Voice input (uses Google)
termux-tts-speak         # Text to speech
termux-clipboard-get/set # Clipboard
termux-contact-list      # Contacts
termux-notification      # Show notification
termux-battery-status    # Battery info
```

**Links:**
- https://f-droid.org/en/packages/com.termux/
- https://f-droid.org/en/packages/com.termux.api/
- https://wiki.termux.com/wiki/Termux:API

---

## Wake Word Options for Android

| Solution | How It Works | Pros | Cons |
|----------|--------------|------|------|
| Wyoming + Termux | Runs openWakeWord in Termux, connects to HA | Full HA integration, OSS | Needs HA server, battery |
| Tasker + AutoVoice | AutoVoice hotword plugin | Works standalone | Not OSS, paid |
| Porcupine | SDK for custom apps | 97% accuracy, background service | Need to build app |
| Dedicated hardware | ESP32, ATOM Echo ($13-30) | Always-on, no phone battery drain | Extra device |

**Wyoming on Termux:**
- https://github.com/pantherale0/wyoming-satellite-termux
- https://community.home-assistant.io/t/how-to-run-wyoming-satellite-and-openwakeword-on-android/777571

---

## Offline STT Options

| Engine | Size | Quality | Notes |
|--------|------|---------|-------|
| Vosk | 50MB+ | Good | Python API, multiple languages |
| Whisper (OpenAI) | 75MB-1.5GB | Excellent | whisper.cpp for local |
| DeepSpeech | 200MB+ | Decent | Mozilla, archived |
| Speech-to-Phrase | Small | Limited vocab | HA optimized |

**Note:** `termux-speech-to-text` uses Google's online STT, so it's not fully open. For offline, need Vosk or Whisper integration.

---

## Architecture Chosen: Termux + Claude

```
┌─────────────────────────────────────────────────────────────┐
│                        Android Phone                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                      Termux                              ││
│  │                                                          ││
│  │  [Wake Word]  →  [STT]  →  [Claude API]  →  [Tools]     ││
│  │   (optional)    (Google/   (tool calling)   (termux-api) ││
│  │                  Vosk)                                   ││
│  │                                     ↓                    ││
│  │                              [TTS Response]              ││
│  │                              (termux-tts-speak)          ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

**Why this approach:**
1. Fully open source (except Google STT, which can be replaced)
2. Direct phone integration (SMS, contacts, clipboard, etc.)
3. Claude's tool calling is perfect for "send SMS to X" type commands
4. Hackable - easy to add new tools
5. Works today with minimal setup

---

## Future Improvements

1. **Offline STT**: Replace Google with Vosk or Whisper
2. **Wake Word**: Integrate Wyoming satellite or Porcupine
3. **More Tools**: Calendar, email, WhatsApp (via Tasker bridge)
4. **Local LLM**: Ollama support for fully offline operation
5. **Home Assistant Bridge**: Connect to HA for home control
6. **Conversation Memory**: Persist context between sessions

---

## Key Links

**Home Assistant:**
- https://www.home-assistant.io/installation
- https://www.home-assistant.io/integrations/anthropic
- https://www.home-assistant.io/voice_control/

**Termux:**
- https://f-droid.org/en/packages/com.termux/
- https://wiki.termux.com/wiki/Termux:API
- https://github.com/pantherale0/wyoming-satellite-termux

**Voice/STT:**
- https://alphacephei.com/vosk/ (Vosk)
- https://picovoice.ai/platform/porcupine/ (Wake word)
- https://github.com/openai/whisper (Whisper)

**Open Assistants:**
- https://github.com/Stypox/dicio-android
- https://github.com/brandall76/Saiy-PS
- https://github.com/OpenVoiceOS
- https://rhasspy.readthedocs.io/

**Claude:**
- https://docs.anthropic.com/en/docs/tool-use
- https://picovoice.ai/blog/add-voice-to-claude/
