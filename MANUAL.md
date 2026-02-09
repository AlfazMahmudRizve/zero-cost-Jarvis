# SHERIFF / JARVIS - SYSTEM MANUAL (v2.0.0)

> **Protocol "Sheriff"**: High-Performance, Zero-Cost, Hybrid AI Omni-Assistant.
> *Local Client + Local/Cloud Brain Architecture.*

---

## 1. System Overview

This system is not a chatbot. It is a **Command & Control Engine** designed to protect your time and focus. It operates on a hybrid architecture:

*   **100% Local Option**: Uses **Ollama** with local LLMs (no API keys needed!)
*   **Cloud Option**: Uses Google Gemini for rapid cloud-based reasoning
*   **Local Processing**: Audio Input, VAD, Wake Word, TTS, PC Automation, Vector Memory

### ⚡ Key Capabilities
-   **Sub-Second Latency**: Optimized 1B parameter model for real-time voice interaction
-   **Persistent Memory**: Remembers conversations across sessions via ChromaDB
-   **Physical Agency**: Controls mouse, keyboard, browser, and system power
-   **Barge-In Support**: Interrupt Jarvis mid-speech by talking
-   **Conversational Mode**: 10-second follow-up window without wake word
-   **Fuzzy Wake Word**: Tolerates mispronunciations (Jarvis/Darius/Jervis)

---

## 2. Installation & Setup

### Requirements
-   **Python 3.10+**
-   **FFmpeg** (Required for audio processing)
    -   `winget install FFmpeg` (Windows)
    -   `brew install ffmpeg` (Mac)
    -   `sudo apt install ffmpeg` (Linux)
-   **Ollama** (Recommended for local LLM)
    -   Download from [https://ollama.ai](https://ollama.ai)

### Deployment Steps

1.  **Clone & Navigate**:
    ```powershell
    cd jarvis
    ```

2.  **Environment Setup**:
    ```powershell
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Install Ollama Model** (Recommended):
    ```powershell
    ollama pull llama3.2:1b
    ```

4.  **Configuration**:
    -   Copy `.env.example` to `.env`
    -   Default uses `LLM_PROVIDER=ollama` (no API key needed!)
    -   *(Optional)*: Change to `LLM_PROVIDER=gemini` and add `GEMINI_API_KEY`

---

## 3. Operational Protocols (How to Use)

### Launch
```powershell
.\run.bat
# or
python main.py
```
*Wait for the "Systems operational" message.*

### The Loop
1.  **Listen**: Wait for voice activity (silence filtering)
2.  **Wake Word**: Say **"JARVIS"** (also accepts "Darius", "Jervis", etc.)
3.  **Acknowledgment**: Jarvis says *"Yes, Sir?"*
4.  **Command**: Give your request
5.  **Response**: Jarvis speaks the answer aloud

### Conversational Mode
After any interaction, you have **10 seconds** to give follow-up commands without saying "Jarvis" again:
-   *"Jarvis, who wrote Hamlet?"* → *"William Shakespeare"*
-   *"When was he born?"* → *"1564"* (no wake word needed!)

### Interruption (Barge-In)
If Jarvis is talking and you want to interrupt:
-   Simply start speaking
-   She will stop immediately and listen
-   Console shows `⏹️ Interrupted!`

### Shutdown
Press `Ctrl+C` in the terminal for graceful shutdown.

---

## 4. Module Deep Dive

### 👂 The Senses (Audio Pipeline)
*   **Input**: `sounddevice` with `numpy`-based VAD
*   **STT (Ears)**: `faster-whisper` running locally on CPU
*   **TTS (Mouth)**: `edge-tts` with interruption support

### 🧠 The Brain (Intelligence)
*   **Ollama (Local)**: `llama3.2:1b` - Fast, private, offline capable
*   **Gemini (Cloud)**: Google Gemini 1.5 Flash - More capable, requires API key
*   **Persona**: "Sheriff" - Authoritative, concise, action-oriented

### 💾 The Hippocampus (Memory)
*   **Technology**: `chromadb` (Local Vector Store)
*   **Function**: Stores every interaction as vector embeddings
*   **Recall**: Provides context-aware responses using semantic search

### 🖐️ The Hands (Tools & Automation)
*   **Browser**: Opens URLs, performs Google searches
*   **Media**: Volume control, play/pause, next/prev track
*   **System**: Lock workstation, (shutdown requires confirmation)

---

## 5. Configuration Reference (.env)

```ini
# LLM Provider: "ollama" (local), "gemini" (cloud), "groq" (cloud)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:1b

# Cloud API Keys (optional if using Ollama)
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here

# Voice Settings
TTS_VOICE=en-US-AriaNeural
TTS_RATE=+10%
WAKE_WORD=jarvis
```

---

## 6. Troubleshooting

**Q: "Brain not connected" / Offline Mode**
A: 
1. If using Ollama: Ensure Ollama is running (`ollama serve`) and model is pulled
2. If using Gemini: Check `GEMINI_API_KEY` in `.env`

**Q: System doesn't hear me / Wake word ignored**
A: 
1. Check microphone settings in Windows
2. Speak clearly: "Jarvis... open Google"
3. System accepts variations: Darius, Jervis, Jarvi, etc.

**Q: Slow responses**
A: 
1. Use smaller model: `ollama pull llama3.2:1b` and set `OLLAMA_MODEL=llama3.2:1b`
2. Or use Gemini cloud for faster inference

**Q: Audio playback fails**
A: Ensure FFmpeg is installed and in PATH

---

## 7. Performance Tips

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| `llama3.2:1b` | 1.3GB | ⚡ Fast | Good |
| `llama3.2` | 2.0GB | Medium | Better |
| `phi3:mini` | 2.3GB | ⚡ Fast | Good |
| Gemini (Cloud) | N/A | ⚡⚡ Fastest | Best |

---

*Built by Alfaz Mahmud Rizve*
