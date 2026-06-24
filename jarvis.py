"""
 ██╗  ██╗███████╗██╗   ██╗    ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
 ██║  ██║██╔════╝╚██╗ ██╔╝    ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
 ███████║█████╗   ╚████╔╝     ██║███████║██████╔╝██║   ██║██║███████╗
 ██╔══██║██╔══╝    ╚██╔╝ ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
 ██║  ██║███████╗   ██║  ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝

 Say "hey jarvis" + clap clap → workspace launches across your screens.
 Built for macOS. GitHub: github.com/YOUR_USERNAME/hey-jarvis
"""

import subprocess
import sys
import time
import numpy as np
import pyaudio
import speech_recognition as sr

# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────

WAKE_WORD = "hey jarvis"
CLAP_THRESHOLD = 2500
CLAP_WINDOW_SECONDS = 6
CLAP_MIN_GAP = 0.15
CLAP_MAX_GAP = 2.0
LISTEN_TIMEOUT = 8

# Spotify: "Should I Stay or Should I Go" — The Clash
SPOTIFY_TRACK_URI = "spotify:track:3v8PlUFGQQDBIk1J86waCo"

# ─────────────────────────────────────────────
#  COLORS
# ─────────────────────────────────────────────

CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def log(msg, color=CYAN):
    print(f"{color}{BOLD}[JARVIS]{RESET} {msg}")

# ─────────────────────────────────────────────
#  SCREEN DETECTION
# ─────────────────────────────────────────────

def get_screens():
    """Returns list of (x, y, width, height) for each screen."""
    try:
        from AppKit import NSScreen
        screens = []
        for screen in NSScreen.screens():
            f = screen.frame()
            screens.append((int(f.origin.x), int(f.origin.y), int(f.size.width), int(f.size.height)))
        return screens
    except Exception:
        log("Could not detect screens — using defaults.", YELLOW)
        return [(0, 0, 1440, 900), (1440, 0, 1920, 1080)]

# ─────────────────────────────────────────────
#  WINDOW MOVER
#  Moves app window to a specific (x, y) position using AppleScript.
#  REQUIRES Accessibility permission for Terminal:
#  → System Settings > Privacy & Security > Accessibility → enable Terminal
# ─────────────────────────────────────────────

def move_window_to(app_name, x, y):
    script = f'''
    tell application "{app_name}" to activate
    delay 0.8
    tell application "System Events"
        tell process "{app_name}"
            try
                set position of window 1 to {{{x}, {y}}}
            end try
        end tell
    end tell
    '''
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if result.returncode != 0 and "not allowed" in result.stderr.lower():
        log("⚠️  Accessibility permission needed to move windows!", RED)
        log("   System Settings → Privacy & Security → Accessibility → enable Terminal", RED)

def hide_app(app_name):
    script = f'tell application "System Events" to set visible of process "{app_name}" to false'
    subprocess.run(['osascript', '-e', script], capture_output=True)

# ─────────────────────────────────────────────
#  APP LAUNCHER
# ─────────────────────────────────────────────

def launch_apps():
    log("Activating your workspace...", GREEN)

    screens = get_screens()

    # Screen 0 = main (mirror) screen
    main_x = screens[0][0] + 40
    main_y = screens[0][1] + 40

    # Screen 1 = extended second screen
    if len(screens) > 1:
        second_x = screens[1][0] + 40
        second_y = screens[1][1] + 40
    else:
        second_x = screens[0][2] + 40
        second_y = 40
        log("Only one screen detected — Cursor will open on the same screen.", YELLOW)

    # 1. Claude → main screen
    subprocess.Popen(["open", "-a", "Claude"])
    log("  ✓ Opened Claude", GREEN)
    time.sleep(1.5)
    move_window_to("Claude", main_x, main_y)
    log("  ✓ Claude placed on main screen", GREEN)

    # 2. Cursor → second screen
    subprocess.Popen(["open", "-a", "Cursor"])
    log("  ✓ Opened Cursor", GREEN)
    time.sleep(2.0)
    move_window_to("Cursor", second_x, second_y)
    log("  ✓ Cursor placed on second screen", GREEN)

    # 3. Spotify → play track, then minimize (music keeps playing)
    subprocess.Popen(["open", "-a", "Spotify"])
    log("  ✓ Opened Spotify", GREEN)
    time.sleep(2.5)
    subprocess.Popen(["open", SPOTIFY_TRACK_URI])
    log("  ✓ Playing: Should I Stay or Should I Go — The Clash 🎸", GREEN)
    time.sleep(1.5)
    hide_app("Spotify")
    log("  ✓ Spotify hidden (music keeps playing)", GREEN)

    log("All systems go. Welcome back.", GREEN)

# ─────────────────────────────────────────────
#  TWO-CLAP DETECTION
# ─────────────────────────────────────────────

def wait_for_two_claps(timeout_seconds=CLAP_WINDOW_SECONDS):
    """Returns True if two claps are detected within timeout_seconds."""
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=44100,
        input=True,
        frames_per_buffer=1024
    )

    log(f"Listening for two claps ({timeout_seconds}s)... 👏👏", YELLOW)
    deadline = time.time() + timeout_seconds
    clap_times = []
    in_clap = False

    try:
        while time.time() < deadline:
            data = stream.read(1024, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.int16)
            peak = np.max(np.abs(samples))

            if peak > CLAP_THRESHOLD and not in_clap:
                now = time.time()
                in_clap = True

                if not clap_times:
                    clap_times.append(now)
                    log("  👏 Clap 1 detected! Clap again...", YELLOW)
                else:
                    gap = now - clap_times[-1]
                    if CLAP_MIN_GAP < gap < CLAP_MAX_GAP:
                        clap_times.append(now)
                        log("  👏 Clap 2 detected!", YELLOW)
                        break
                    elif gap >= CLAP_MAX_GAP:
                        clap_times = [now]
                        log("  Too slow — clap 1 reset. Clap again...", YELLOW)

            elif peak <= CLAP_THRESHOLD:
                in_clap = False

            if len(clap_times) >= 2:
                break

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    return len(clap_times) >= 2

# ─────────────────────────────────────────────
#  WAKE WORD DETECTION
# ─────────────────────────────────────────────

def listen_for_wake_word():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    log("Calibrating microphone for ambient noise...", YELLOW)
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
    log(f'Ready. Say "{WAKE_WORD}" to launch your workspace.', CYAN)
    print()

    while True:
        try:
            with mic as source:
                audio = recognizer.listen(source, timeout=LISTEN_TIMEOUT, phrase_time_limit=4)

            text = recognizer.recognize_google(audio).lower()
            log(f'Heard: "{text}"', YELLOW)

            if WAKE_WORD in text:
                log("Wake word detected! Launching...", GREEN)
                launch_apps()
                print()
                log(f'Back to listening. Say "{WAKE_WORD}" again anytime.', CYAN)

        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            log(f"Speech recognition error: {e}", RED)
            log("Check your internet connection.", RED)
            time.sleep(3)
        except KeyboardInterrupt:
            print()
            log("Shutting down. Goodbye!", CYAN)
            sys.exit(0)

# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print(f"{CYAN}{BOLD}{'─'*50}")
    print("  HEY JARVIS — Personal Workspace Launcher")
    print(f"{'─'*50}{RESET}")
    print()
    listen_for_wake_word()
