# 🤖 Zero-Cost JARVIS

> **A fully local, privacy-first AI voice assistant for Windows**  
> Built by [Alfaz Mahmud Rizve](https://github.com/AlfazMahmudRizve)

![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-green?style=for-the-badge)
![Windows](https://img.shields.io/badge/Windows-11-blue?style=for-the-badge&logo=windows)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

---

## ⚡ What is Zero-Cost JARVIS?

A **voice-controlled AI assistant** that runs entirely on your PC — no API keys, no cloud costs, no data leaving your machine.

| Feature | Description |
|---------|-------------|
| 🎤 **Voice Control** | Speak naturally, JARVIS listens and responds |
| 🧠 **Local LLM** | Powered by Ollama (Qwen 2.5) — fully offline |
| 🔊 **Natural Speech** | Microsoft Edge TTS for human-like voice |
| 💻 **PC Control** | Open apps, control volume, browse web |
| 🔒 **Privacy First** | Everything stays on your machine |

---

## 🎬 Demo

```
You: "Jarvis, open Spotify"
JARVIS: "Opening Spotify."

You: "Jarvis, what's the weather like?"
JARVIS: "I don't have internet access, but you can check weather.com, Sir."

You: "Jarvis, goodbye"
JARVIS: "Goodbye, Sir." *exits*
```

---

## 🚀 Quick Start

### Prerequisites
- **Windows 10/11**
- **Python 3.12+**
- **[Ollama](https://ollama.ai)** installed
- **Microphone**

### Installation

```bash
# Clone the repo
git clone https://github.com/AlfazMahmudRizve/zero-cost-Jarvis.git
cd zero-cost-Jarvis

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Pull the LLM model
ollama pull qwen2.5:3b

# Run JARVIS
.\run.bat
```

---

## 🎤 Voice Commands

| Say This | JARVIS Does |
|----------|-------------|
| *"Jarvis, open Chrome"* | Launches Chrome browser |
| *"Jarvis, open Spotify"* | Opens Spotify |
| *"Jarvis, volume up"* | Increases system volume |
| *"Jarvis, search for Python tutorials"* | Google search |
| *"Jarvis, lock my PC"* | Locks workstation |
| *"Jarvis, what time is it?"* | Tells the time |
| *"Jarvis, goodbye"* | Shuts down JARVIS |

### Supported Apps
Chrome, Firefox, Edge, VSCode, Notepad, Word, Excel, PowerPoint, Discord, Slack, Teams, Spotify, VLC, Steam, Calculator, File Explorer, and more!

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    JARVIS CORE                          │
├─────────────────────────────────────────────────────────┤
│  🎤 EARS          │ Faster-Whisper (Local STT)          │
│  🧠 BRAIN         │ Ollama Qwen 2.5 (Local LLM)         │
│  💾 MEMORY        │ ChromaDB (Vector Store)             │
│  🔊 MOUTH         │ Edge-TTS (Speech Synthesis)         │
│  🖐️ HANDS         │ PyAutoGUI + PowerShell (PC Control) │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuration

Edit `.env` to customize:

```env
# LLM
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:3b

# Voice
TTS_VOICE=en-US-GuyNeural
TTS_RATE=+10%

# Speech Recognition
WHISPER_MODEL_SIZE=base
```

---

## 🛡️ Privacy & Safety

- ✅ **100% Local** — No cloud APIs required
- ✅ **No Data Collection** — Your voice stays on your PC
- ✅ **No PC Shutdown** — Can't turn off your computer
- ✅ **Failsafe Mode** — Move mouse to corner to stop

---

## 📁 Project Structure

```
jarvis/
├── main.py              # Entry point
├── run.bat              # Windows launcher
├── .env                 # Configuration
├── src/
│   ├── brain/           # LLM + prompts
│   ├── senses/          # Audio, STT, TTS
│   ├── memory/          # Vector database
│   ├── tools/           # PC automation
│   └── core/            # Config, logging
└── requirements.txt
```

---

## 🤝 Contributing

Pull requests welcome! For major changes, open an issue first.

---

## 📜 License

MIT License - see [LICENSE](LICENSE)

---

## 👨‍💻 Author

**Alfaz Mahmud Rizve**  
- GitHub: [@AlfazMahmudRizve](https://github.com/AlfazMahmudRizve)
- Website: [whoisalfaz.me](https://whoisalfaz.me)

---

<p align="center">
  <b>Built with ❤️ for the open-source community</b>
</p>
