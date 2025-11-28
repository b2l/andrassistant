#!/usr/bin/env python3
"""
Termux + Claude Voice Assistant

A voice assistant for Android that uses:
- Termux:API for phone integration (SMS, TTS, STT)
- Claude API for intelligent responses and tool use
- Local file storage for notes

Requirements:
- Termux + Termux:API from F-Droid
- Python packages: anthropic
- Environment variable: ANTHROPIC_API_KEY
"""

import subprocess
import json
import os
from datetime import datetime
from anthropic import Anthropic

# Initialize Claude client
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Directory for storing notes
NOTES_DIR = os.path.expanduser("~/notes")
os.makedirs(NOTES_DIR, exist_ok=True)

# Define tools that Claude can use
TOOLS = [
    {
        "name": "send_sms",
        "description": "Send an SMS text message to a phone number",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "Phone number with country code (e.g., +1234567890)"
                },
                "message": {
                    "type": "string",
                    "description": "The message content to send"
                }
            },
            "required": ["phone_number", "message"]
        }
    },
    {
        "name": "read_sms",
        "description": "Read recent SMS messages from the phone",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of messages to read (default: 5)",
                    "default": 5
                },
                "from_number": {
                    "type": "string",
                    "description": "Filter messages from a specific phone number (optional)"
                }
            }
        }
    },
    {
        "name": "write_note",
        "description": "Save a note to a file for later reference",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The note content to save"
                },
                "filename": {
                    "type": "string",
                    "description": "Optional filename (without extension). If not provided, uses timestamp."
                },
                "append": {
                    "type": "boolean",
                    "description": "If true, append to existing file instead of overwriting",
                    "default": False
                }
            },
            "required": ["content"]
        }
    },
    {
        "name": "read_notes",
        "description": "Read saved notes from storage",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Specific note filename to read (optional, reads recent if not specified)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of recent notes to read if no filename specified",
                    "default": 5
                }
            }
        }
    },
    {
        "name": "list_notes",
        "description": "List all saved note files",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "delete_note",
        "description": "Delete a specific note file",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The filename of the note to delete"
                }
            },
            "required": ["filename"]
        }
    },
    {
        "name": "get_clipboard",
        "description": "Get the current contents of the clipboard",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "set_clipboard",
        "description": "Set text to the clipboard",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to copy to clipboard"
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "get_battery_status",
        "description": "Get the current battery level and charging status",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "show_notification",
        "description": "Display a notification on the phone",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Notification title"
                },
                "content": {
                    "type": "string",
                    "description": "Notification content/body"
                }
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "get_contacts",
        "description": "Search contacts by name",
        "input_schema": {
            "type": "object",
            "properties": {
                "search": {
                    "type": "string",
                    "description": "Name to search for in contacts"
                }
            },
            "required": ["search"]
        }
    }
]

SYSTEM_PROMPT = """You are a helpful voice assistant running on an Android phone via Termux.

Your capabilities:
- Send and read SMS messages
- Take, read, list, and delete notes
- Access clipboard
- Show notifications
- Check battery status
- Search contacts

Guidelines:
- Keep responses concise and suitable for voice output (1-2 sentences when possible)
- When the user asks to do something, use the appropriate tool
- Always confirm actions briefly after completing them
- If a request is ambiguous, ask for clarification
- For SMS, if no phone number is given, try to find the contact first
- Be proactive in offering relevant follow-up actions

Remember: Your responses will be spoken aloud, so avoid technical jargon and keep it natural."""


def run_termux_command(args: list, input_text: str = None) -> tuple[int, str, str]:
    """Run a termux command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            input=input_text,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def execute_tool(name: str, args: dict) -> str:
    """Execute a tool and return the result."""

    if name == "send_sms":
        phone = args["phone_number"]
        message = args["message"]
        returncode, stdout, stderr = run_termux_command(
            ["termux-sms-send", "-n", phone, message]
        )
        if returncode == 0:
            return f"SMS sent successfully to {phone}"
        return f"Failed to send SMS: {stderr}"

    elif name == "read_sms":
        limit = args.get("limit", 5)
        cmd = ["termux-sms-list", "-l", str(limit)]

        returncode, stdout, stderr = run_termux_command(cmd)
        if returncode != 0:
            return f"Error reading SMS: {stderr}"

        try:
            messages = json.loads(stdout)
            from_number = args.get("from_number")

            if from_number:
                messages = [m for m in messages if from_number in m.get("number", "")]

            if not messages:
                return "No messages found"

            formatted = []
            for msg in messages:
                sender = msg.get("number", "Unknown")
                body = msg.get("body", "")
                date = msg.get("received", "")
                formatted.append(f"From {sender} ({date}):\n{body}")

            return "\n\n---\n\n".join(formatted)
        except json.JSONDecodeError:
            return f"Error parsing SMS data: {stdout}"

    elif name == "write_note":
        content = args["content"]
        filename = args.get("filename", datetime.now().strftime("%Y%m%d_%H%M%S"))
        if not filename.endswith(".txt"):
            filename += ".txt"

        filepath = os.path.join(NOTES_DIR, filename)
        mode = "a" if args.get("append", False) else "w"

        try:
            with open(filepath, mode) as f:
                if mode == "a" and os.path.getsize(filepath) > 0:
                    f.write("\n\n")
                f.write(content)
            return f"Note saved to {filename}"
        except Exception as e:
            return f"Error saving note: {e}"

    elif name == "read_notes":
        filename = args.get("filename")

        if filename:
            if not filename.endswith(".txt"):
                filename += ".txt"
            filepath = os.path.join(NOTES_DIR, filename)
            try:
                with open(filepath) as f:
                    return f"=== {filename} ===\n{f.read()}"
            except FileNotFoundError:
                return f"Note '{filename}' not found"
            except Exception as e:
                return f"Error reading note: {e}"
        else:
            # Read recent notes
            limit = args.get("limit", 5)
            try:
                files = sorted(os.listdir(NOTES_DIR), reverse=True)[:limit]
                if not files:
                    return "No notes found"

                notes = []
                for f in files:
                    with open(os.path.join(NOTES_DIR, f)) as file:
                        notes.append(f"=== {f} ===\n{file.read()}")
                return "\n\n".join(notes)
            except Exception as e:
                return f"Error reading notes: {e}"

    elif name == "list_notes":
        try:
            files = sorted(os.listdir(NOTES_DIR), reverse=True)
            if not files:
                return "No notes saved yet"
            return "Saved notes:\n" + "\n".join(f"- {f}" for f in files)
        except Exception as e:
            return f"Error listing notes: {e}"

    elif name == "delete_note":
        filename = args["filename"]
        if not filename.endswith(".txt"):
            filename += ".txt"
        filepath = os.path.join(NOTES_DIR, filename)

        try:
            os.remove(filepath)
            return f"Note '{filename}' deleted"
        except FileNotFoundError:
            return f"Note '{filename}' not found"
        except Exception as e:
            return f"Error deleting note: {e}"

    elif name == "get_clipboard":
        returncode, stdout, stderr = run_termux_command(["termux-clipboard-get"])
        if returncode == 0:
            return f"Clipboard contents: {stdout}" if stdout else "Clipboard is empty"
        return f"Error reading clipboard: {stderr}"

    elif name == "set_clipboard":
        text = args["text"]
        returncode, stdout, stderr = run_termux_command(
            ["termux-clipboard-set", text]
        )
        if returncode == 0:
            return "Text copied to clipboard"
        return f"Error setting clipboard: {stderr}"

    elif name == "get_battery_status":
        returncode, stdout, stderr = run_termux_command(["termux-battery-status"])
        if returncode != 0:
            return f"Error getting battery status: {stderr}"

        try:
            status = json.loads(stdout)
            percentage = status.get("percentage", "unknown")
            plugged = status.get("plugged", "UNKNOWN")
            charging = "charging" if plugged != "UNPLUGGED" else "not charging"
            return f"Battery is at {percentage}% and {charging}"
        except json.JSONDecodeError:
            return f"Error parsing battery status: {stdout}"

    elif name == "show_notification":
        title = args["title"]
        content = args["content"]
        returncode, stdout, stderr = run_termux_command([
            "termux-notification",
            "--title", title,
            "--content", content
        ])
        if returncode == 0:
            return "Notification displayed"
        return f"Error showing notification: {stderr}"

    elif name == "get_contacts":
        search = args["search"].lower()
        returncode, stdout, stderr = run_termux_command(["termux-contact-list"])

        if returncode != 0:
            return f"Error reading contacts: {stderr}"

        try:
            contacts = json.loads(stdout)
            matches = [
                c for c in contacts
                if search in c.get("name", "").lower()
            ]

            if not matches:
                return f"No contacts found matching '{args['search']}'"

            formatted = []
            for c in matches[:5]:  # Limit to 5 results
                name = c.get("name", "Unknown")
                number = c.get("number", "No number")
                formatted.append(f"{name}: {number}")

            return "Contacts found:\n" + "\n".join(formatted)
        except json.JSONDecodeError:
            return f"Error parsing contacts: {stdout}"

    return f"Unknown tool: {name}"


def listen() -> str:
    """Get speech input from user using Android's speech recognition."""
    print("\n[Listening... speak now]")

    returncode, stdout, stderr = run_termux_command(
        ["termux-speech-to-text"],
        input_text=None
    )

    text = stdout.strip()

    if returncode != 0 or not text:
        print("[No speech detected]")
        return ""

    print(f"You: {text}")
    return text


def speak(text: str):
    """Speak text aloud using Android's TTS."""
    print(f"Assistant: {text}")
    run_termux_command(["termux-tts-speak", text])


def chat(user_input: str, history: list) -> str:
    """Send message to Claude and handle tool calls."""

    history.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=history
    )

    # Handle tool use loop
    while response.stop_reason == "tool_use":
        tool_results = []
        assistant_content = response.content

        for block in response.content:
            if block.type == "tool_use":
                print(f"[Executing: {block.name}]")
                result = execute_tool(block.name, block.input)
                print(f"[Result: {result[:100]}{'...' if len(result) > 100 else ''}]")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        history.append({"role": "assistant", "content": assistant_content})
        history.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=history
        )

    # Extract text response
    assistant_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            assistant_text += block.text

    history.append({"role": "assistant", "content": response.content})
    return assistant_text


def text_mode():
    """Run in text input mode (for testing without voice)."""
    print("=== Termux Assistant (Text Mode) ===")
    print("Type 'quit' to exit, 'voice' to switch to voice mode\n")

    history = []

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "quit":
                print("Goodbye!")
                break

            if user_input.lower() == "voice":
                return voice_mode()

            response = chat(user_input, history)
            print(f"Assistant: {response}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


def voice_mode():
    """Run in voice input/output mode."""
    print("=== Termux Assistant (Voice Mode) ===")
    print("Say 'quit' to exit, 'text mode' to switch to text input\n")

    speak("Hello, I'm ready to help.")
    history = []

    while True:
        try:
            user_input = listen()

            if not user_input:
                speak("I didn't catch that. Please try again.")
                continue

            lower_input = user_input.lower()

            if lower_input in ["quit", "exit", "stop", "goodbye"]:
                speak("Goodbye!")
                break

            if "text mode" in lower_input:
                print("Switching to text mode...")
                return text_mode()

            response = chat(user_input, history)
            speak(response)

        except KeyboardInterrupt:
            speak("Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            speak("Sorry, something went wrong. Please try again.")


def main():
    """Main entry point."""
    import sys

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Run: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    # Parse command line arguments
    mode = "text"  # Default to text mode for easier testing

    if len(sys.argv) > 1:
        if sys.argv[1] in ["-v", "--voice"]:
            mode = "voice"
        elif sys.argv[1] in ["-t", "--text"]:
            mode = "text"
        elif sys.argv[1] in ["-h", "--help"]:
            print("Usage: assistant.py [OPTIONS]")
            print("  -v, --voice    Start in voice mode")
            print("  -t, --text     Start in text mode (default)")
            print("  -h, --help     Show this help")
            sys.exit(0)

    if mode == "voice":
        voice_mode()
    else:
        text_mode()


if __name__ == "__main__":
    main()
