# 🤖 Hey Jarvis — Personal Workspace Launcher

> Say **"Hey Jarvis"**  → your entire workspace opens instantly.

Inspired by Iron Man's J.A.R.V.I.S., this is a lightweight Python script that runs silently in the background on your Mac. When it hears your wake phrase followed by a clap, it launches all your go-to apps at once — no clicking, no hunting, just voice + clap.

---

## What it launches

By default:
- **Claude** (AI assistant)
- **Brave Browser**
- **Spotify**
- **Cursor** (AI code editor)

You can customize the app list in 10 seconds — just edit the `APPS` list in `jarvis.py`.

---

## How it works

1. The script listens passively via your microphone
2. You say **"Hey Jarvis"**
3. It prompts you to clap within 5 seconds
4. Clap detected → all apps launch simultaneously

The clap acts as a confirmation so it doesn't fire from TV audio or other voices saying "hey jarvis." Smart, not just reactive.

---

## Setup

### Requirements
- macOS (uses the `open -a` command)
- Python 3.8+
- Internet connection (uses Google's free Speech Recognition API)

### Install

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/hey-jarvis.git
cd hey-jarvis

# Install dependencies
pip install -r requirements.txt

# If pyaudio fails to install on macOS, run this first:
brew install portaudio
pip install pyaudio
```

### Run

```bash
python jarvis.py
```

On first launch, macOS will ask for **microphone permission** — allow it.

---

## Customize

Open `jarvis.py` and edit the config block at the top:

```python
WAKE_WORD = "hey jarvis"      # Change your trigger phrase
CLAP_THRESHOLD = 2500          # Lower = more sensitive to claps
CLAP_WINDOW_SECONDS = 5        # How long to wait for clap after wake word

APPS = [
    "Claude",
    "Brave Browser",
    "Spotify",
    "Cursor",
    # Add any macOS app here — must match the name in /Applications
]
```

---

## Run on startup (optional)

To have Jarvis always listening when you turn on your Mac:

```bash
# Create a launch agent
cp com.yourname.jarvis.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.yourname.jarvis.plist
```

*(A starter `.plist` file for this is coming soon.)*

---

## Dependencies

| Library | Purpose |
|---|---|
| `SpeechRecognition` | Converts microphone audio to text |
| `pyaudio` | Raw microphone access for clap detection |
| `numpy` | Measures audio amplitude peaks |

---

## Why I built this

I got tired of clicking around every morning to set up my workspace. Iron Man had Jarvis boot everything up — I wanted that. Turns out it takes less than 100 lines of Python.

---

## Contributing

PRs welcome. Ideas for next versions:
- [ ] Offline wake word detection (no internet required)
- [ ] Windows support
- [ ] Custom launch sequences (morning mode vs. work mode vs. creative mode)
- [ ] Voice feedback ("Good morning, launching your workspace...")

---

Built with Python on macOS. Zero paid APIs.
