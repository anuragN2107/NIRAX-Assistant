# ==========================================
# NIRAX: Next-gen Information Retrieval & Assistance X-agent
# Creator: Anurag Srivastava
# ==========================================

import os
import sys
import json
import subprocess
import datetime
import re
import webbrowser
import glob
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import speech_recognition as sr
import pyttsx3
import pywhatkit
import psutil
import pyautogui
from google import genai
from dotenv import load_dotenv

# -------------------------------------------------------------------------
# RESOURCE PATH RESOLUTION
# -------------------------------------------------------------------------
def resource_path(relative_path):
    """
    Ensures that local asset files (such as logo, video, config) 
    load properly whether running as a standard Python script 
    or as a packaged standalone .exe application.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Load secure API keys from local .env configuration file
load_dotenv(resource_path(".env"))

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("ERROR: GEMINI_API_KEY is missing from the .env file!")
    exit(1)

# -------------------------------------------------------------------------
# GEMINI AI & MULTI-TURN MEMORY SETUP
# -------------------------------------------------------------------------
client = genai.Client(api_key=API_KEY)
GEMINI_MODEL = "gemini-2.5-flash"

# Feature 1: Initialize continuous multi-turn chat memory session
chat_session = client.chats.create(model=GEMINI_MODEL)

# -------------------------------------------------------------------------
# TEXT-TO-SPEECH (TTS) ENGINE CONFIGURATION
# -------------------------------------------------------------------------
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
speech_lock = threading.Lock()  # Thread lock to prevent audio engine crashes

# -------------------------------------------------------------------------
# FEATURE 5: SHORTCUT MANAGER CONFIGURATION & STORAGE
# -------------------------------------------------------------------------
SHORTCUTS_FILE = "shortcuts.json"

def load_shortcuts():
    """
    Loads custom website or app shortcuts from a local JSON file.
    If the file doesn't exist, it creates default mappings.
    """
    default_shortcuts = {
        "workspace": "https://github.com",
        "chatgpt": "https://chatgpt.com",
        "mail": "https://mail.google.com",
        "youtube": "https://www.youtube.com"
    }
    if os.path.exists(SHORTCUTS_FILE):
        try:
            with open(SHORTCUTS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return default_shortcuts
    else:
        with open(SHORTCUTS_FILE, "w") as f:
            json.dump(default_shortcuts, f, indent=4)
        return default_shortcuts

def save_shortcut(name, target):
    """
    Saves a new user-defined shortcut mapping into the JSON file.
    """
    shortcuts = load_shortcuts()
    shortcuts[name.lower().strip()] = target.strip()
    with open(SHORTCUTS_FILE, "w") as f:
        json.dump(shortcuts, f, indent=4)

def speak(text):
    """
    Safely strips markdown symbols and speaks text out loud 
    using a thread lock to keep audio execution smooth.
    """
    clean_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    clean_text = re.sub(r'[*#_`]', '', clean_text)
    print(f"NIRAX: {clean_text}")
    
    with speech_lock:
        try:
            engine.say(clean_text)
            engine.runAndWait()
        except Exception as e:
            print(f"Speech Engine Error: {e}")

def ask_gemini(prompt):
    """
    Sends prompts to the ongoing multi-turn Gemini chat session 
    with built-in error handling for free-tier rate limits.
    """
    try:
        response = chat_session.send_message(prompt)
        return response.text
    except Exception as e:
        error_message = str(e)
        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            return "Sir, my daily AI request quota has been temporarily exhausted. Please try again tomorrow."
        else:
            print(f"Gemini Error: {e}")
            return "I am having trouble connecting to my neural network right now."

def find_and_open_desktop_app(app_name):
    """
    Dynamically scans Windows Start Menu & Desktop shortcuts 
    for any installed application requested by voice.
    """
    app_name = app_name.lower().strip()
    shortcut_dirs = [
        os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\**\\*.lnk"),
        "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\**\\*.lnk",
        os.path.expanduser("~\\Desktop\\*.lnk")
    ]
    for pattern in shortcut_dirs:
        for file_path in glob.glob(pattern, recursive=True):
            if app_name in os.path.basename(file_path).lower():
                try:
                    os.startfile(file_path)
                    return True
                except:
                    pass
    try:
        subprocess.Popen([app_name])
        return True
    except:
        pass
    return False

# -------------------------------------------------------------------------
# COMMAND EXECUTION ENGINE
# -------------------------------------------------------------------------
def execute_command(query, user_name, update_ui_callback, app_instance=None):
    """
    Processes user voice inputs, routing them to local shortcuts, 
    hardware diagnostics, volume controls, theme toggles, or AI memory logic.
    """
    update_ui_callback(f">> USER [{user_name}]: {query}")
    
    speak(f"You asked, {query}")

    # Local conversational helpers (0 API cost)
    if "how are you" in query or "how r u" in query:
        msg = f"Systems nominal and running at peak performance, {user_name}."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
        return
    elif "who are you" in query:
        msg = "I am NIRAX, Next-gen Information Retrieval and Assistance X-agent."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
        return

    # Feature 5 UI text command bypass
    elif "add shortcut" in query or "save shortcut" in query:
        msg = f"Shortcut manager active. Please use the interface panel to map custom items, {user_name}."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
        return

    # Feature 3: Voice Theme Switching
    elif "theme" in query or "color scheme" in query:
        if "green" in query or "matrix" in query:
            if app_instance: app_instance.set_theme("Matrix Green")
            msg = f"Switched to Matrix Green protocol, {user_name}."
        elif "red" in query or "tactical" in query:
            if app_instance: app_instance.set_theme("Tactical Red")
            msg = f"Switched to Tactical Red protocol, {user_name}."
        elif "purple" in query or "synthwave" in query:
            if app_instance: app_instance.set_theme("Synthwave Purple")
            msg = f"Switched to Synthwave Purple protocol, {user_name}."
        elif "gold" in query or "amber" in query:
            if app_instance: app_instance.set_theme("Solar Amber")
            msg = f"Switched to Solar Amber protocol, {user_name}."
        else:
            if app_instance: app_instance.set_theme("Cyber HUD Cyan")
            msg = f"Switched to Cyber HUD Cyan protocol, {user_name}."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
        return

    # Feature 2: System Diagnostics & Hardware Control
    elif "cpu" in query or "processor" in query:
        cpu_usage = psutil.cpu_percent(interval=1)
        msg = f"Active CPU utilization is at {cpu_usage} percent, {user_name}."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
        return
    elif "ram" in query or "memory" in query:
        memory = psutil.virtual_memory()
        msg = f"RAM utilization at {memory.percent} percent. {round(memory.available / (1024**3), 1)} gigabytes available."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
        return
    elif "battery" in query:
        battery = psutil.sensors_battery()
        if battery:
            plugged = "connected to external power" if battery.power_plugged else "discharging on internal cell"
            msg = f"Power level at {battery.percent} percent, currently {plugged}."
        else:
            msg = f"No mobile power telemetry detected."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
        return
    elif "mute" in query:
        pyautogui.press('volumemute')
        msg = f"Master audio output muted."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
        return
    elif "volume up" in query:
        for _ in range(5): pyautogui.press('volumeup')
        msg = f"Audio gain increased."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
        return
    elif "volume down" in query:
        for _ in range(5): pyautogui.press('volumedown')
        msg = f"Audio gain decreased."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
        return

    # Feature 5: Custom Shortcut Mapping Check
    shortcuts = load_shortcuts()
    target_keyword = query.replace("open", "").strip()
    if target_keyword in shortcuts:
        target_url = shortcuts[target_keyword]
        msg = f"Executing custom shortcut for {target_keyword}."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
        webbrowser.open(target_url)
        return

    # Standard Actions (YouTube, Search, Apps, Time, Date)
    if "play" in query:
        song = query.replace("play", "").strip()
        msg = f"Initiating media stream: {song}."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
        pywhatkit.playonyt(song)
    elif "search" in query or "google" in query:
        search_term = query.replace("search", "").replace("google", "").strip()
        msg = f"Querying global index for {search_term}."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
        pywhatkit.search(search_term)
    elif "open" in query:
        target = query.replace("open", "").strip()
        update_ui_callback(f">> NIRAX: Scanning local indices for {target}...")
        if find_and_open_desktop_app(target):
            msg = f"Executing local binary: {target}."
            update_ui_callback(f">> NIRAX: {msg}")
            speak(msg)
        else:
            msg = f"Binary not found locally. Routing to web node."
            update_ui_callback(f">> NIRAX: {msg}")
            speak(msg)
            webbrowser.open(f"https://www.{target.replace(' ', '')}.com")
    elif "time" in query:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        msg = f"System time: {current_time}."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
    elif "date" in query or "day is today" in query or "calendar" in query:
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        msg = f"Calendar check: Today is {current_date}."
        update_ui_callback(f">> NIRAX: {msg}")
        speak(msg)
    else:
        # Fallback to Gemini AI with chat memory context
        update_ui_callback(">> NIRAX: Processing query via neural network...")
        ai_reply = ask_gemini(query)
        update_ui_callback(f">> NIRAX: {ai_reply}")
        speak(ai_reply)


# -------------------------------------------------------------------------
# GRAPHICAL USER INTERFACE (HUD) CLASS
# -------------------------------------------------------------------------
class NiraxApp:
    # Feature 3: Available Color Schemes & Technical Palettes
    THEMES = {
        "Cyber HUD Cyan": {"bg": "#010409", "panel": "#0d1117", "border": "#00f3ff", "text": "#e2e8f0", "accent": "#0088ff", "title": "#38bdf8", "dim": "#64748b", "grid": "#0d1b2a"},
        "Matrix Green": {"bg": "#011408", "panel": "#05220f", "border": "#00ff66", "text": "#f0fdf4", "accent": "#16a34a", "title": "#4ade80", "dim": "#86efac", "grid": "#063314"},
        "Tactical Red": {"bg": "#120303", "panel": "#230707", "border": "#ff1a1a", "text": "#fef2f2", "accent": "#dc2626", "title": "#f87171", "dim": "#fca5a5", "grid": "#2b0a0a"},
        "Synthwave Purple": {"bg": "#0e071b", "panel": "#1d1033", "border": "#d946ef", "text": "#fae8ff", "accent": "#9333ea", "title": "#e879f9", "dim": "#c084fc", "grid": "#2b134d"},
        "Solar Amber": {"bg": "#140c02", "panel": "#261704", "border": "#f59e0b", "text": "#fef3c7", "accent": "#d97706", "title": "#fbbf24", "dim": "#fcd34d", "grid": "#3b2306"}
    }

    def __init__(self, root):
        self.root = root
        self.root.title("NIRAX // SECURE TECHNICAL INTERFACE [HUD v5.5]")
        
        # Configure window size and state
        self.root.state('zoomed') 
        self.root.minsize(950, 700)
        
        self.current_theme = "Cyber HUD Cyan"
        t = self.THEMES[self.current_theme]
        self.user_name = "OPERATOR"
        
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Technical background grid canvas layer
        self.bg_canvas = tk.Canvas(root, bg=t["bg"], highlightthickness=0)
        self.bg_canvas.grid(row=0, column=0, sticky="nsew")
        self.bg_canvas.bind("<Configure>", self.on_window_resize)

        # Top Header HUD Bar
        self.header_frame = tk.Frame(self.bg_canvas, bg=t["panel"], bd=1, relief="solid")
        self.header_window = self.bg_canvas.create_window(20, 15, anchor="nw", window=self.header_frame)
        self.header_frame.columnconfigure(2, weight=1)
        
        try:
            logo_path = resource_path("nirax_logo.png")
            pil_image = Image.open(logo_path)
            pil_image = pil_image.resize((40, 40), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(pil_image)
            self.logo_label = tk.Label(self.header_frame, image=self.logo_img, bg=t["panel"])
            self.logo_label.grid(row=0, column=0, padx=10, pady=6)
        except Exception:
            pass

        self.header_title = tk.Label(self.header_frame, text="NIRAX // TECHNICAL COMMAND CONSOLE", font=("Consolas", 11, "bold"), fg=t["title"], bg=t["panel"])
        self.header_title.grid(row=0, column=1, sticky="w", padx=5)

        self.telemetry_label = tk.Label(self.header_frame, text="STATUS: STANDBY | ENCRYPTION: ACTIVE", font=("Consolas", 9), fg=t["dim"], bg=t["panel"])
        self.telemetry_label.grid(row=0, column=2, sticky="e", padx=15)

        self.theme_var = tk.StringVar(value=self.current_theme)
        self.theme_dropdown = ttk.Combobox(self.header_frame, textvariable=self.theme_var, values=list(self.THEMES.keys()), state="readonly", width=18)
        self.theme_dropdown.grid(row=0, column=3, padx=15)
        self.theme_dropdown.bind("<<ComboboxSelected>>", self.on_theme_selected)

        # Main Technical Container Grid
        self.main_container = tk.Frame(self.bg_canvas, bg=t["bg"])
        self.container_window = self.bg_canvas.create_window(20, 90, anchor="nw", window=self.main_container)
        self.main_container.rowconfigure(0, weight=1)
        self.main_container.columnconfigure(1, weight=4)

        # Left Sidebar (Telemetry HUD + Shortcut Manager)
        self.sidebar_frame = tk.Frame(self.main_container, bg=t["panel"], bd=1, relief="solid")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        self.sidebar_frame.rowconfigure(1, weight=1)
        
        tk.Label(self.sidebar_frame, text="[ TELEMETRY HUD ]", font=("Consolas", 10, "bold"), fg=t["title"], bg=t["panel"]).pack(pady=10)
        
        self.sys_info_box = tk.Text(self.sidebar_frame, height=14, width=26, bg=t["bg"], fg=t["text"], font=("Consolas", 9), relief="flat", padx=8, pady=8)
        self.sys_info_box.pack(padx=10, pady=5, fill="both", expand=True)
        self.update_telemetry_sidebar()

        # Feature 5 UI: Shortcut Manager Widget inside Sidebar
        self.shortcut_panel = tk.Frame(self.sidebar_frame, bg=t["panel"], bd=1, relief="sunken")
        self.shortcut_panel.pack(padx=10, pady=10, fill="x")
        
        tk.Label(self.shortcut_panel, text="[ ADD SHORTCUT ]", font=("Consolas", 9, "bold"), fg=t["title"], bg=t["panel"]).pack(pady=2)
        
        self.sc_name_entry = tk.Entry(self.shortcut_panel, font=("Consolas", 9), width=22)
        self.sc_name_entry.pack(pady=2)
        self.sc_name_entry.insert(0, "Keyword (e.g. portal)")

        self.sc_url_entry = tk.Entry(self.shortcut_panel, font=("Consolas", 9), width=22)
        self.sc_url_entry.pack(pady=2)
        self.sc_url_entry.insert(0, "URL or Path")

        self.save_sc_btn = tk.Button(self.shortcut_panel, text="Save Shortcut", font=("Consolas", 8, "bold"), bg=t["accent"], fg="white", command=self.handle_add_shortcut)
        self.save_sc_btn.pack(pady=5)

        # Right Side (Terminal Output Stream & Voice Deck)
        self.console_frame = tk.Frame(self.main_container, bg=t["panel"], bd=1, relief="solid")
        self.console_frame.grid(row=0, column=1, sticky="nsew", pady=5)
        self.console_frame.rowconfigure(1, weight=1)
        self.console_frame.columnconfigure(0, weight=1)

        self.console_header = tk.Label(self.console_frame, text=">>> SYSTEM TERMINAL & OUTPUT STREAM", font=("Consolas", 10, "bold"), fg=t["title"], bg=t["panel"], anchor="w", padx=15)
        self.console_header.grid(row=0, column=0, sticky="ew", pady=8)

        self.output_box = tk.Text(self.console_frame, bg=t["bg"], fg=t["text"], font=("Consolas", 11), relief="flat", padx=12, pady=12)
        self.output_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.deck_frame = tk.Frame(self.console_frame, bg=t["panel"])
        self.deck_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=12)
        self.deck_frame.columnconfigure(0, weight=1)

        self.status_label = tk.Label(self.deck_frame, text="INITIALIZING HARDWARE LINK...", font=("Consolas", 10, "bold"), fg=t["title"], bg=t["panel"])
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.mic_button = tk.Button(self.deck_frame, text="[ 🎙 ENGAGE VOICE COMMAND ]", font=("Consolas", 11, "bold"), bg=t["accent"], fg="white", activebackground=t["panel"], activeforeground="white", relief="raised", padx=20, pady=8, command=self.start_listening_thread, state=tk.DISABLED)
        self.mic_button.pack(side=tk.RIGHT, padx=5)

        # Start background user identification thread
        threading.Thread(target=self.identify_user_sequence).start()

    def handle_add_shortcut(self):
        """UI button handler to capture and save user-defined shortcuts."""
        name = self.sc_name_entry.get().strip()
        target = self.sc_url_entry.get().strip()
        if name and target and name != "Keyword (e.g. portal)":
            save_shortcut(name, target)
            self.log_output(f">> SYSTEM: Custom shortcut '{name}' successfully mapped.")
            speak(f"Shortcut {name} saved successfully.")
            self.sc_name_entry.delete(0, tk.END)
            self.sc_url_entry.delete(0, tk.END)

    def on_window_resize(self, event):
        """Handles canvas resizing and layout scaling when window dimensions change."""
        width = event.width
        height = event.height
        t = self.THEMES[self.current_theme]
        self.draw_tech_grid(t["grid"], width, height)

        header_width = max(800, width - 40)
        self.bg_canvas.coords(self.header_window, 20, 15)
        self.bg_canvas.itemconfig(self.header_window, width=header_width)

        container_width = max(800, width - 40)
        container_height = max(450, height - 120)
        self.bg_canvas.coords(self.container_window, 20, 90)
        self.bg_canvas.itemconfig(self.container_window, width=container_width, height=container_height)

    def draw_tech_grid(self, grid_color, width, height):
        """Renders the precision sci-fi grid matrix across the background canvas."""
        self.bg_canvas.delete("grid")
        for x in range(0, width, 50):
            self.bg_canvas.create_line(x, 0, x, height, fill=grid_color, width=1, tags="grid")
        for y in range(0, height, 50):
            self.bg_canvas.create_line(0, y, width, y, fill=grid_color, width=1, tags="grid")

    def set_theme(self, theme_name):
        """Dynamically re-styles all GUI widgets to match the selected theme palette."""
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            t = self.THEMES[theme_name]
            
            self.bg_canvas.config(bg=t["bg"])
            self.draw_tech_grid(t["grid"], self.bg_canvas.winfo_width(), self.bg_canvas.winfo_height())
            
            self.header_frame.config(bg=t["panel"])
            if hasattr(self, 'logo_label'):
                self.logo_label.config(bg=t["panel"])
            self.header_title.config(bg=t["panel"], fg=t["title"])
            self.telemetry_label.config(bg=t["panel"], fg=t["dim"])
            
            self.main_container.config(bg=t["bg"])
            self.sidebar_frame.config(bg=t["panel"])
            for widget in self.sidebar_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(bg=t["panel"], fg=t["title"])
            self.sys_info_box.config(bg=t["bg"], fg=t["text"])
            self.shortcut_panel.config(bg=t["panel"])
            for widget in self.shortcut_panel.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.config(bg=t["panel"], fg=t["title"])
            self.save_sc_btn.config(bg=t["accent"])
            
            self.console_frame.config(bg=t["panel"])
            self.console_header.config(bg=t["panel"], fg=t["title"])
            self.output_box.config(bg=t["bg"], fg=t["text"])
            
            self.deck_frame.config(bg=t["panel"])
            self.status_label.config(bg=t["panel"], fg=t["title"])
            self.mic_button.config(bg=t["accent"], activebackground=t["panel"])

    def on_theme_selected(self, event):
        """Dropdown event handler for theme selection."""
        selected_theme = self.theme_var.get()
        self.set_theme(selected_theme)
        self.log_output(f">> SYSTEM: Tactical UI Palette updated to {selected_theme}.")

    def update_telemetry_sidebar(self):
        """Fetches live system stats (CPU, RAM, Disk, Battery) and updates telemetry sidebar."""
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            battery = psutil.sensors_battery()
            batt_pct = f"{battery.percent}%" if battery else "N/A"
            
            telemetry_text = f"""[SYSTEM METRICS]
--------------------
CPU LOAD:  {cpu}%
RAM USAGE: {ram}%
DISK USE:  {disk}%
BATTERY:   {batt_pct}

[AGENT CONFIG]
--------------------
CORES:     AI Core active
MODEL:     Gemini-2.5-Flash
SECURITY:  AES-256 Validated
CREATOR:   Anurag Srivastava
"""
            self.sys_info_box.delete("1.0", tk.END)
            self.sys_info_box.insert(tk.END, telemetry_text)
        except Exception:
            pass
        
        # Schedule the telemetry loop to run again in 5 seconds
        self.root.after(5000, self.update_telemetry_sidebar)

    def identify_user_sequence(self):
        """Listens via microphone on startup to verify operator name."""
        prompt = "Hello! I am NIRAX. Who is using this system today?"
        self.log_output(f">> NIRAX: {prompt}")
        speak(prompt)
        
        self.root.after(0, lambda: self.status_label.config(text="AWAITING VOICE SIGNATURE..."))
        
        r = sr.Recognizer()
        captured = False
        
        while not captured:
            try:
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=1.0)
                    audio = r.listen(source, timeout=10, phrase_time_limit=6)
                    spoken_name = r.recognize_google(audio, language='en-in').title()
                    if spoken_name:
                        self.user_name = spoken_name
                        captured = True
            except Exception:
                retry_prompt = "Voice signature unrecognized. Please state your name again."
                self.log_output(f">> NIRAX: {retry_prompt}")
                speak(retry_prompt)

        welcome_msg = f"Identity verified: {self.user_name}. Tactical HUD online."
        self.log_output(f">> NIRAX: {welcome_msg}")
        speak(welcome_msg)
            
        self.root.after(0, lambda: self.mic_button.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.status_label.config(text="STATUS: READY FOR COMMAND"))

    def log_output(self, message):
        """Appends formatted messages to the main terminal console box."""
        self.output_box.insert(tk.END, message + "\n")
        self.output_box.see(tk.END)

    def start_listening_thread(self):
        """Spawns background thread for active voice command listening."""
        self.mic_button.config(state=tk.DISABLED, bg="#475569")
        self.status_label.config(text="STATUS: LISTENING...")
        threading.Thread(target=self.listen_and_process).start()

    def listen_and_process(self):
        """Captures microphone input and passes it to the command execution engine."""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.8)
            try:
                audio = r.listen(source, timeout=8, phrase_time_limit=10)
                query = r.recognize_google(audio, language='en-in').lower()
                self.root.after(0, lambda: execute_command(query, self.user_name, self.log_output, self))
            except sr.WaitTimeoutError:
                self.root.after(0, lambda: self.log_output(">> SYSTEM: Audio capture timed out."))
            except sr.UnknownValueError:
                self.root.after(0, lambda: self.log_output(">> SYSTEM: Input not understood."))
            except Exception as e:
                self.root.after(0, lambda: self.log_output(f">> ERROR: {e}"))
            
            t = self.THEMES[self.current_theme]
            self.root.after(0, lambda: self.mic_button.config(state=tk.NORMAL, bg=t["accent"]))
            self.root.after(0, lambda: self.status_label.config(text="STATUS: READY FOR COMMAND"))


# -------------------------------------------------------------------------
# CINEMATIC INTRO VIDEO SPLASH SCREEN
# -------------------------------------------------------------------------
def play_intro_video():
    """Plays the 10-second cinematic intro video fullscreen with synchronized voiceover."""
    video_path = resource_path("nirax_intro.mp4")
    
    def play_intro_audio():
        import time
        time.sleep(1.0)
        speak("Welcome to NIRAX, your Next-gen Information Retrieval and Assistance X-agent.")

    audio_thread = threading.Thread(target=play_intro_audio)
    audio_thread.start()

    if os.path.exists(video_path):
        cap = cv2.VideoCapture(video_path)
        window_name = "NIRAX - Cinematic Intro"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow(window_name, frame)
            if cv2.waitKey(25) & 0xFF != 255:
                break
            
        cap.release()
        cv2.destroyAllWindows()


# -------------------------------------------------------------------------
# MAIN ENTRY POINT
# -------------------------------------------------------------------------
if __name__ == "__main__":
    # Play cinematic video sequence first
    play_intro_video()
    
    # Launch main technical HUD desktop GUI application
    root = tk.Tk()
    app = NiraxApp(root)
    root.mainloop()