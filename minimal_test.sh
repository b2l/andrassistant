#!/bin/bash
#
# Minimal voice assistant test - NO Claude, NO Python
# Tests the core Termux:API functionality
#
# Install:
#   1. Install Termux + Termux:API from F-Droid
#   2. pkg install termux-api
#   3. Grant permissions (SMS, Microphone, Contacts)
#   4. Run this script
#

echo "=== Minimal Voice Assistant Test ==="
echo "Testing Termux:API without Claude"
echo ""

# Simple command loop
while true; do
    echo ""
    echo "Say a command (or type 'quit' to exit)..."

    # Get voice input
    INPUT=$(termux-speech-to-text 2>/dev/null)

    if [ -z "$INPUT" ]; then
        termux-tts-speak "I didn't catch that"
        continue
    fi

    echo "You said: $INPUT"

    # Convert to lowercase for matching
    CMD=$(echo "$INPUT" | tr '[:upper:]' '[:lower:]')

    # Simple pattern matching
    case "$CMD" in
        *quit*|*exit*|*stop*)
            termux-tts-speak "Goodbye!"
            exit 0
            ;;
        *battery*)
            LEVEL=$(termux-battery-status | grep -o '"percentage":[0-9]*' | cut -d: -f2)
            termux-tts-speak "Battery is at $LEVEL percent"
            ;;
        *time*)
            TIME=$(date +"%I:%M %p")
            termux-tts-speak "The time is $TIME"
            ;;
        *date*)
            DATE=$(date +"%A, %B %d")
            termux-tts-speak "Today is $DATE"
            ;;
        *read*message*|*read*sms*|*read*text*)
            echo "Reading last SMS..."
            MSG=$(termux-sms-list -l 1 2>/dev/null)
            if [ -n "$MSG" ]; then
                SENDER=$(echo "$MSG" | grep -o '"number":"[^"]*"' | head -1 | cut -d'"' -f4)
                BODY=$(echo "$MSG" | grep -o '"body":"[^"]*"' | head -1 | cut -d'"' -f4)
                termux-tts-speak "Message from $SENDER: $BODY"
            else
                termux-tts-speak "No messages found or permission denied"
            fi
            ;;
        *clipboard*)
            CLIP=$(termux-clipboard-get)
            if [ -n "$CLIP" ]; then
                termux-tts-speak "Clipboard contains: $CLIP"
            else
                termux-tts-speak "Clipboard is empty"
            fi
            ;;
        *note*|*remember*)
            # Extract everything after "note" or "remember"
            NOTE=$(echo "$INPUT" | sed -E 's/.*(note|remember)[[:space:]]*//')
            if [ -n "$NOTE" ]; then
                mkdir -p ~/notes
                FILENAME=~/notes/$(date +%Y%m%d_%H%M%S).txt
                echo "$NOTE" > "$FILENAME"
                termux-tts-speak "Note saved"
            else
                termux-tts-speak "What should I note?"
            fi
            ;;
        *help*)
            termux-tts-speak "Commands: battery, time, date, read messages, clipboard, note something, or quit"
            ;;
        *)
            termux-tts-speak "I don't understand. Say help for commands."
            ;;
    esac
done
