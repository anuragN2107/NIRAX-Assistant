<p align="center">
  <img src="nirax_logo.png" alt="NIRAX Logo" width="220" height="220">
</p>

<h1 align="center">NIRAX</h1>
<p align="center"><b>Next-gen Information Retrieval & Assistance X-agent</b></p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-00f3ff?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.10%2B-38bdf8?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Gemini-2.5%20Flash-4ade80?style=flat-square&logo=google&logoColor=white" alt="Gemini AI">
  <img src="https://img.shields.io/badge/License-MIT-9333ea?style=flat-square" alt="License">
</p>

---

## 🚀 Overview
**NIRAX** is an advanced, production-grade desktop AI assistant engineered from the ground up by **Anurag Srivastava**. It bridges natural language processing (Google Gemini LLM), system hardware telemetry diagnostics, custom voice-controlled execution, dynamic app/web launching, and real-time visual UI telemetry into a unified, high-performance desktop software suite.

---

## ✨ Core Features & Technical Capabilities

1. **🧠 Multi-Turn Chat Memory:** Built using Google's GenAI SDK chat sessions (`client.chats.create`), maintaining ongoing conversational context across back-to-back prompts.
2. **💻 Live System Diagnostics & Hardware Control:** Real-time monitoring of CPU load, RAM utilization, storage metrics, and battery status via `psutil`, alongside voice-activated Windows master volume controls (`pyautogui`).
3. **🎨 Designer Technical HUD & Theme Switcher:** Fully responsive, full-scale tactical interface featuring a dynamic sci-fi grid canvas and 5 instant theme palettes (*Cyber HUD Cyan, Matrix Green, Tactical Red, Synthwave Purple, and Solar Amber*).
4. **🔗 Custom App & Website Shortcut Manager:** Integrated JSON-backed shortcut mapper (`shortcuts.json`) allowing users to add and execute custom voice-activated web portals instantly.
5. **🎬 Cinematic Intro & Voiceover Sequence:** Fullscreen OpenCV video splash screen (`nirax_intro.mp4`) with synchronized text-to-speech welcome greetings.
6. **🎙 Interactive Voice Recognition:** Click-to-speak voice command deck utilizing Google Speech-to-Text and threaded `pyttsx3` text-to-speech synthesis.

---

## 🛠️ Tech Stack & Architecture
* **GUI & Interface:** Python `tkinter`, `ttk`, `Pillow (PIL)`, `tk.Canvas`
* **Artificial Intelligence:** Google GenAI SDK (`google-genai` using `gemini-2.5-flash`)
* **Voice & Audio Processing:** `speech_recognition`, `pyttsx3` (with thread locking)
* **System Automation:** `psutil`, `pyautogui`, `webbrowser`, `pywhatkit`, `subprocess`
* **Security & Distribution:** `python-dotenv`, `PyInstaller`, OpenCV (`cv2`)

---

## ⚙️ Installation & Setup Guide

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/NIRAX-Virtual-Assistant.git](https://github.com/YOUR_USERNAME/NIRAX-Virtual-Assistant.git)
cd NIRAX-Virtual-Assistant
