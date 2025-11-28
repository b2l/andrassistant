#!/bin/bash
#
# Test script to verify Termux:API is working correctly
# Run this before using the assistant to ensure all permissions are set up
#

echo "=== Termux:API Test Suite ==="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Check if termux-api package is installed
echo "Checking termux-api package..."
if command -v termux-battery-status &> /dev/null; then
    pass "termux-api package is installed"
else
    fail "termux-api package not found. Run: pkg install termux-api"
    exit 1
fi

echo ""
echo "Testing API commands (some may prompt for permissions)..."
echo ""

# Test battery status (no special permissions needed)
echo "1. Battery Status..."
if termux-battery-status > /dev/null 2>&1; then
    BATTERY=$(termux-battery-status | grep -o '"percentage":[0-9]*' | cut -d: -f2)
    pass "Battery status works (${BATTERY}%)"
else
    fail "Battery status failed"
fi

# Test TTS
echo "2. Text-to-Speech..."
if termux-tts-speak "Test" 2>/dev/null; then
    pass "TTS works"
else
    warn "TTS may not be available"
fi

# Test clipboard
echo "3. Clipboard..."
TEST_TEXT="termux_test_$(date +%s)"
termux-clipboard-set "$TEST_TEXT" 2>/dev/null
CLIP=$(termux-clipboard-get 2>/dev/null)
if [ "$CLIP" = "$TEST_TEXT" ]; then
    pass "Clipboard read/write works"
else
    fail "Clipboard failed"
fi

# Test toast
echo "4. Toast notification..."
if termux-toast "API Test" 2>/dev/null; then
    pass "Toast works"
else
    warn "Toast may not work"
fi

# Test SMS list (needs permission)
echo "5. SMS Access..."
if termux-sms-list -l 1 > /dev/null 2>&1; then
    pass "SMS read access works"
else
    warn "SMS access denied - grant permission in Android Settings"
fi

# Test contacts (needs permission)
echo "6. Contacts Access..."
if termux-contact-list > /dev/null 2>&1; then
    CONTACT_COUNT=$(termux-contact-list 2>/dev/null | grep -c '"name"' || echo "0")
    pass "Contacts access works ($CONTACT_COUNT contacts)"
else
    warn "Contacts access denied - grant permission in Android Settings"
fi

# Test notification (needs permission)
echo "7. Notifications..."
if termux-notification --title "Test" --content "API Test" 2>/dev/null; then
    pass "Notifications work"
    termux-notification-remove --id "test" 2>/dev/null
else
    warn "Notifications may require permission"
fi

# Test speech-to-text (needs Google + microphone)
echo "8. Speech-to-Text..."
echo "   (Skipping interactive test - requires microphone)"
warn "Run 'termux-speech-to-text' manually to test voice input"

echo ""
echo "=== Test Complete ==="
echo ""
echo "If any tests failed, check:"
echo "1. Termux:API app is installed from F-Droid"
echo "2. Permissions are granted in Android Settings → Apps → Termux:API"
echo "3. For STT: Google app is installed and enabled"
echo ""
