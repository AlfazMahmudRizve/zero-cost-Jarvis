# SHERIFF / JARVIS - SYSTEM MANUAL (v3.0.0)

> **Protocol "Sheriff"**: High-Performance, Zero-Cost, Autonomous AI Assistant.
> *Fully Local Brain & Senses Architecture.*

---

## 1. System Overview

This system is a **Local Command & Control Engine** designed for privacy, speed, and autonomy. It has evolved from a cloud-dependent chatbot into a fully self-hosted agent.

### 🧠 Core Architecture
*   **Brain**: **Ollama** running `qwen2.5:7b` (Local, Uncensored, Free)
*   **Ears**: `faster-whisper` (Local, High Accuracy, Noise Filtering)
*   **Mouth**: `edge-tts` (High Quality Neural Voice) with `pygame` playback
*   **Body**: `pyautogui` & `subprocess` for full system control

### ⚡ Key Capabilities
-   **Wake Word Variants**: Responds to "Sheriff", "Jarvis", "Service", "Harvest" (mishearing tolerant).
-   **Noise Filtering**: Ignores short sounds (<2 chars) and requires 1s silence to activate.
-   **Deep App Integration**: Launches Spotify/YouTube Music to specific songs via deep links.
-   **System Control**: Clipboard access, typing, key presses, file management.
-   **Project Awareness**: Knows workspace structure (`spectre`, `CashOps`, etc.).
-   **Zero Interruption**: Enforces full sentence completion to prevent self-interruption feedback loops.

---

## 2. Tech Stack & Evolution

### Current Stack (v3.0)
-   **Language**: Python 3.12
-   **LLM**: Qwen 2.5 (7B Parameters) via Ollama
-   **STT**: Faster-Whisper (CUDA/CPU) with VAD (Voice Activity Detection)
-   **TTS**: Edge-TTS -> Pygame Mixer
-   **Tools**: Custom Function Calling Engine (JSON-based)

### Development History
1.  **Phase 1 (Gemini Cloud)**:
    -   Initial build using Google Gemini 1.5 Flash.
    -   Fast but hit API rate limits and privacy concerns.
    -   Reliant on internet connection.

2.  **Phase 2 (Hybrid)**:
    -   Introduced local STT/TTS.
    -   Gemini for reasoning, local for sensing.
    -   Added basic tools (File I/O).

3.  **Phase 3 (Fully Local - Current)**:
    -   Migrated Brain to **Ollama** (`qwen2.5:7b`).
    -   Rewrote `llm.py` to handle tool calling via JSON prompting (since local models lack native function calling).
    -   Implemented "Sheriff" persona with strict protocol.
    -   Added "Superpowers": Music playback, Clipboard reading, Typing.
    -   Hardened stability (Noise filtering, TTS buffers).

---

## 3. Operational Protocols

### Launch
```powershell
.\run.bat
```
*Wait for "Ready for your command, Sheriff."*

### Voice Commands
1.  **Wake Word**: Say **"Sheriff"** (or "Jarvis", "Service")
2.  **Command**: Speak naturally.
    -   *"Sheriff, play Blinding Lights"* (Opens Spotify)
    -   *"Service, what's in my clipboard?"*
    -   *"Harvest, run git status"*
    -   *"Jarvis, check the spectre project"*

### Music Control
-   **Spotify**: Uses URI protocol `spotify:search:{song}` to launch app.
-   **YouTube Music**: Uses browser to search `music.youtube.com`.

### Shutdown
-   Voice: *"Sheriff, goodbye"*
-   Manual: `Ctrl+C` in terminal.

---

## 4. Configuration (.env)

```ini
# Core Brain
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b

# Senses
WAKE_WORD=jarvis  (Triggers on synonyms too)
TTS_VOICE=en-US-AriaNeural
WHISPER_MODEL=base

# Paths
WORKSPACE_ROOT=E:/Ai Agents/whoisalfaz.me/Web Projects/antigravity
```

---

## 5. Troubleshooting

**Q: "Brain not connected"**
-   Ensure Ollama is running: `ollama serve`
-   Verify model exists: `ollama list`

**Q: Doesn't hear me**
-   Speak louder; VAD threshold is strict to prevent noise triggers.
-   Wait 1 second after TTS finishes before speaking.

**Q: Plays music but doesn't auto-start**
-   Limitation of Spotify Free API. We use Deep Links to get you to the song immediately.

---

*Built by Alfaz Mahmud Rizve*
