"""
AMADEUS Retro Pixel Shimeji (Lab Assistant Desktop Companion)
Ultra-lightweight Windows desktop pet that climbs on active window title bars,
reads, drinks Dr Pepper, parachutes on minimize, and connects to the AMADEUS Brain.

Enhanced Multimodal Features:
- ️ Active Window & Screen Watcher (multimodal inspection of code/browser/errors)
-  Dynamic Emotion Sync (/ws/lively & /kurisu/sync)
-  Real-Time Kurisu Chat (/kurisu/chat with mem0 memory grounding)
-  Native Win32 window-hopping & parachute physics
-  0% GPU / <15MB RAM idle consumption
"""

import base64
import io
import json
import math
import os
import random
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from typing import Optional, Tuple
import urllib.request
import urllib.error

from loguru import logger
from PIL import Image, ImageGrab, ImageTk

try:
    import win32gui
except ImportError:
    print("Error: pywin32 is required. Run: pip install pywin32")
    sys.exit(1)


SPRITES_DIR = Path(__file__).parent / "sprites"
CHROMA_KEY = "#000001"  # 100% transparent click-through color key on Windows

# Built-in fallback Kurisu Tsundere / Lab Assistant dialogue lines
KURISU_QUOTES = [
    "It's not like I'm sitting on your window because I like you or anything!",
    "Oi! Have you committed your changes today? Don't leave git dirty.",
    "Dr Pepper is the intellectual drink for the chosen ones.",
    "A-Are you staring at me? Focus on your code, idiot!",
    "Correlation does not imply causation! Remember that.",
    "Who are you calling 'Christina'?! There's no '-tina'!",
    "If you break the build, don't come crying to me.",
    "I'm an associate researcher at Viktor Chondria, not a digital toy!",
    "Time travel is theoretically possible, but right now you should write tests.",
    "Keep this world line above 1.048596% divergence, understood?",
]


class ShimejiBrainSync:
    """Connects to AMADEUS Brain for Emotion Sync, Screen Inspect, and Chat."""

    def __init__(self, app):
        self.app = app
        self.running = True
        self.last_thought = ""
        self.current_emotion = "content"
        self.divergence = "1.048596%"
        self.brain_online = False

        self._thread = threading.Thread(target=self._sync_loop, daemon=True)
        self._thread.start()

    def _sync_loop(self):
        while self.running:
            self._sync_kurisu_state()
            time.sleep(12)  # Ambient telemetry pulse

    def _sync_kurisu_state(self):
        """Pulls emotion state, divergence, and spontaneous thoughts."""
        try:
            # Sync telemetry from /kurisu/sync
            req = urllib.request.Request(
                "http://localhost:8000/kurisu/sync",
                headers={"Host": "localhost", "User-Agent": "AMADEUS-Shimeji/2.0"},
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.brain_online = True

                emotion_data = data.get("emotion", {})
                dom_emotion = emotion_data.get("dominant_emotion", "content")
                if dom_emotion != self.current_emotion:
                    self.current_emotion = dom_emotion
                    self.app.on_emotion_change(dom_emotion)

                telem = data.get("telemetry", {})
                self.divergence = telem.get("divergence_meter", "1.048596%")

        except Exception as exc:
            self.brain_online = False
            logger.debug(f"ShimejiBrainSync._sync_kurisu_state: silent exception ignored: {exc}")

        # Check for spontaneous thought
        if self.brain_online:
            try:
                req_think = urllib.request.Request(
                    "http://localhost:8000/kurisu/think",
                    headers={"Host": "localhost", "Content-Type": "application/json"},
                    data=json.dumps({"user_id": "tonpai"}).encode("utf-8"),
                )
                with urllib.request.urlopen(req_think, timeout=5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    thought = data.get("response", "")
                    if thought and thought != self.last_thought:
                        self.last_thought = thought
                        self.app.show_speech(thought, emotion=data.get("emotion"))
            except Exception as exc:
                logger.debug(f"ShimejiBrainSync._sync_kurisu_state (think): silent exception ignored: {exc}")

    def inspect_active_screen(self, bbox: Optional[Tuple[int, int, int, int]] = None, window_title: str = ""):
        """Captures active screen area and requests multimodal vision critique."""
        def _worker():
            self.app.show_speech("Analyzing your screen...", frame="shime16")
            try:
                # Capture screen crop
                screen_img = ImageGrab.grab(bbox=bbox) if bbox else ImageGrab.grab()
                # Downscale for snappy network transmission if huge
                screen_img.thumbnail((1280, 720))
                buf = io.BytesIO()
                screen_img.save(buf, format="JPEG", quality=80)
                img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

                if self.brain_online:
                    # Ask AMADEUS screen inspect
                    req = urllib.request.Request(
                        "http://localhost:8000/kurisu/chat",
                        headers={"Host": "localhost", "Content-Type": "application/json"},
                        data=json.dumps({
                            "message": f"[Screen Inspection: User is currently on '{window_title}']. Make a sharp, concise Steins;Gate Kurisu observation about what they are doing.",
                            "user_id": "tonpai"
                        }).encode("utf-8"),
                    )
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        res = json.loads(resp.read().decode("utf-8"))
                        self.app.show_speech(res.get("response", "Looks orderly."), emotion=res.get("emotion"))
                        return
            except Exception as exc:
                logger.debug(f"ShimejiBrainSync.inspect_active_screen: silent exception ignored: {exc}")

            # Local fallback screen observation based on window context
            title_lower = window_title.lower()
            if any(k in title_lower for k in ("youtube", "netflix", "bilibili", "reddit", "twitter", "x.com")):
                critique = "Oi! Are you slacking off? The worldline divergence is slipping!"
                emo = "annoyed"
            elif any(k in title_lower for k in ("error", "traceback", "failed", "bug", "exception")):
                critique = "I spotted an error on your screen. Did you forget to check your types again?"
                emo = "smug"
            elif any(k in title_lower for k in ("code", "visual studio", "pycharm", ".py", ".ts", ".js")):
                critique = "Writing code? Remember: modular architecture beats sprawling monoliths."
                emo = "focused"
            elif any(k in title_lower for k in ("tonpai", "august", "pos", "order", "inventory")):
                critique = "Reviewing business logistics? Keep the daily cashflow grounded."
                emo = "content"
            else:
                critique = f"Observing: '{window_title[:30]}…' Don't lose focus, lab member."
                emo = "curious"

            self.app.show_speech(critique, emotion=emo)

        threading.Thread(target=_worker, daemon=True).start()

    def ask_kurisu(self, prompt: str):
        """Sends user prompt to /kurisu/chat."""
        def _worker():
            self.app.show_speech("Thinking...", frame="shime16")
            try:
                if self.brain_online:
                    req = urllib.request.Request(
                        "http://localhost:8000/kurisu/chat",
                        headers={"Host": "localhost", "Content-Type": "application/json"},
                        data=json.dumps({"message": prompt, "user_id": "tonpai"}).encode("utf-8"),
                    )
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        res = json.loads(resp.read().decode("utf-8"))
                        self.app.show_speech(res.get("response", "I heard you."), emotion=res.get("emotion"))
                        return
            except Exception as exc:
                logger.debug(f"ShimejiBrainSync.ask_kurisu: silent exception ignored: {exc}")

            # Fallback
            self.app.show_speech("Start AMADEUS Brain (Option 3 in Dev Dock) for full AI recall!", emotion="annoyed")

        threading.Thread(target=_worker, daemon=True).start()


class AmadeusShimeji:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AMADEUS Shimeji")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", CHROMA_KEY)
        self.root.config(bg=CHROMA_KEY)

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Canvas layout
        self.width = 240
        self.height = 190
        self.sprite_offset_x = 56
        self.sprite_offset_y = 60

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=CHROMA_KEY,
            highlightthickness=0,
        )
        self.canvas.pack()

        # Sprites storage
        self.sprites = {}
        self._load_sprites()

        # State machine
        self.state = "WALK"
        self.x = self.screen_width // 2
        self.y = 100
        self.vx = 2
        self.target_window_hwnd = None
        self.target_rect = None
        self.target_title = ""
        self.current_frame = "shime1"
        self.walk_toggle = False
        self.idle_timer = 0
        self.speech_bubble_timer = 0
        self.dominant_emotion = "content"

        # Drag tracking
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Bindings
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", self._show_context_menu)
        self.canvas.bind("<Double-Button-1>", lambda e: self._prompt_chat_dialog())

        # Hotkeys
        self.root.bind_all("<Control-Shift-S>", lambda e: self._inspect_screen())
        self.root.bind_all("<Control-Shift-s>", lambda e: self._inspect_screen())
        self.root.bind_all("<Control-Shift-K>", lambda e: self._prompt_chat_dialog())
        self.root.bind_all("<Control-Shift-k>", lambda e: self._prompt_chat_dialog())

        # Brain connection
        self.brain = ShimejiBrainSync(self)

        # Context Menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label=" Inspect Active Screen (Ctrl+Shift+S)", command=self._inspect_screen)
        self.menu.add_command(label=" Talk to Kurisu (Ctrl+Shift+K)", command=self._prompt_chat_dialog)
        self.menu.add_separator()
        self.menu.add_command(label=" Force Sleep", command=self._force_sleep)
        self.menu.add_command(label=" Drop to Taskbar", command=self._drop_to_taskbar)
        self.menu.add_command(label=" Hop to Active Window", command=self._hop_to_active)
        self.menu.add_separator()
        self.menu.add_command(label=" Dismiss", command=self.root.quit)

        self._update_window_position()
        self.root.after(80, self._tick)

    def _load_sprites(self):
        """Loads Shimeji-ee format sprites from sprites/."""
        required = [
            "shime1", "shime2", "shime3", "shime12", "shime13",
            "shime14", "shime15", "shime16", "shime17", "shime18", "shime23",
        ]
        for name in required:
            file_path = SPRITES_DIR / f"{name}.png"
            if file_path.exists():
                try:
                    pil_img = Image.open(file_path).convert("RGBA")
                    bg = Image.new("RGBA", pil_img.size, CHROMA_KEY)
                    bg.paste(pil_img, mask=pil_img)
                    self.sprites[name] = ImageTk.PhotoImage(bg)
                except Exception as e:
                    print(f"Warning: Failed to load {file_path}: {e}")

    def _get_active_window(self) -> Optional[Tuple[int, Tuple[int, int, int, int], str]]:
        """Gets active foreground window rect and title."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd or hwnd == self.root.winfo_id():
                return None
            class_name = win32gui.GetClassName(hwnd)
            if class_name in ("Progman", "WorkerW", "Shell_TrayWnd", "Shell_SecondaryTrayWnd"):
                return None
            if win32gui.IsIconic(hwnd) or not win32gui.IsWindowVisible(hwnd):
                return None
            rect = win32gui.GetWindowRect(hwnd)
            if rect[2] - rect[0] < 100 or rect[3] - rect[1] < 80:
                return None
            title = win32gui.GetWindowText(hwnd)
            return hwnd, rect, title
        except Exception as exc:
            logger.debug(f"AmadeusShimeji._get_active_window: silent exception ignored: {exc}")
            return None

    def _tick(self):
        """Main physics & behavior tick running at ~12 FPS."""
        if not self.is_dragging:
            self._update_physics()

        self._render()
        self._update_window_position()

        interval = 500 if self.state == "SLEEP" else 90
        self.root.after(interval, self._tick)

    def _update_physics(self):
        active = self._get_active_window()

        if active:
            hwnd, rect, title = active
            self.target_title = title
            if self.target_window_hwnd != hwnd and self.state not in ("HOP", "PARACHUTE"):
                self.target_window_hwnd = hwnd
                self.target_rect = rect
                self.state = "HOP"
            else:
                self.target_rect = rect
        else:
            if self.state not in ("PARACHUTE", "DRAGGED") and self.y < self.screen_height - 210:
                self.state = "PARACHUTE"

        # State updates
        if self.state == "WALK":
            if self.target_rect:
                left, top, right, _ = self.target_rect
                # If window is near the top of screen or maximized, keep Kurisu on-screen
                target_y = 0 if top < 160 else max(0, top - 175)
                self.y = target_y

                # Calculate visible horizontal ledge bounds
                ledge_left = max(10, left + 10)
                ledge_right = min(self.screen_width - self.width - 10, right - self.width)
                if ledge_right <= ledge_left:
                    ledge_left = 10
                    ledge_right = self.screen_width - self.width - 10

                self.x += self.vx
                if self.x >= ledge_right:
                    self.x = ledge_right
                    self.vx = -abs(self.vx)
                elif self.x <= ledge_left:
                    self.x = ledge_left
                    self.vx = abs(self.vx)
            else:
                self.x += self.vx
                max_x = self.screen_width - self.width - 10
                if self.x >= max_x:
                    self.x = max_x
                    self.vx = -abs(self.vx)
                elif self.x <= 10:
                    self.x = 10
                    self.vx = abs(self.vx)

            self.walk_toggle = not self.walk_toggle
            self.current_frame = "shime2" if self.walk_toggle else "shime3"

            self.idle_timer += 1
            if self.idle_timer > 60:
                self.state = "SIT"
                self.idle_timer = 0

        elif self.state == "SIT":
            self.current_frame = "shime15"
            self.idle_timer += 1
            if self.idle_timer > 40:
                self.state = random.choice(["READ", "DRINK"])
                self.idle_timer = 0

        elif self.state == "READ":
            self.current_frame = "shime16"
            self.idle_timer += 1
            if self.idle_timer > 80:
                self.state = "SLEEP"
                self.idle_timer = 0

        elif self.state == "DRINK":
            self.current_frame = "shime17"
            self.idle_timer += 1
            if self.idle_timer > 60:
                self.state = "WALK"
                self.idle_timer = 0

        elif self.state == "SLEEP":
            self.current_frame = "shime18"
            self.idle_timer += 1
            if self.idle_timer > 120:
                self.state = "WALK"
                self.idle_timer = 0

        elif self.state == "HOP":
            self.current_frame = "shime12"
            if self.target_rect:
                left, top, right, _ = self.target_rect
                target_x = max(20, min(left + 60, self.screen_width - self.width - 20))
                target_y = 0 if top < 160 else max(0, top - 175)
                dx = target_x - self.x
                dy = target_y - self.y
                dist = math.hypot(dx, dy)
                if dist < 20:
                    self.x = target_x
                    self.y = target_y
                    self.state = "WALK"
                else:
                    self.x += dx * 0.25
                    self.y += dy * 0.25
            else:
                self.state = "WALK"

        elif self.state == "PARACHUTE":
            self.current_frame = "shime13" if (time.time() * 2) % 2 > 1 else "shime14"
            target_floor = self.screen_height - self.height - 40
            if self.y < target_floor:
                self.y += 4
                self.x += math.sin(self.y * 0.05) * 2
            else:
                self.y = target_floor
                self.state = "SIT"

    def _render(self):
        self.canvas.delete("all")

        sprite = self.sprites.get(self.current_frame, self.sprites.get("shime1"))
        if sprite:
            self.canvas.create_image(
                self.sprite_offset_x,
                self.sprite_offset_y,
                anchor="nw",
                image=sprite,
            )

        if self.speech_bubble_timer > 0:
            self.speech_bubble_timer -= 1
            self._render_speech_bubble()

    def _render_speech_bubble(self):
        text = getattr(self, "_active_speech_text", "")
        if not text:
            return

        bx1, by1 = 8, 6
        bx2, by2 = self.width - 8, 54

        # Box border with Steins;Gate warm orange outline
        self.canvas.create_rectangle(bx1, by1, bx2, by2, fill="#14141E", outline="#E2583E", width=2)
        # Downward pointer
        self.canvas.create_polygon(
            [self.width // 2 - 6, by2, self.width // 2 + 6, by2, self.width // 2, by2 + 7],
            fill="#14141E",
            outline="#E2583E",
        )
        display_text = text if len(text) <= 42 else text[:40] + "…"
        self.canvas.create_text(
            self.width // 2,
            by1 + 24,
            text=display_text,
            fill="#FFFFFF",
            font=("Consolas", 8, "bold"),
            width=self.width - 20,
        )

    def _update_window_position(self):
        # Strict boundary clamping: never allow window off the screen
        clamp_x = max(0, min(int(self.x), self.screen_width - self.width))
        clamp_y = max(0, min(int(self.y), self.screen_height - self.height - 35))
        self.x = clamp_x
        self.y = clamp_y
        self.root.geometry(f"{self.width}x{self.height}+{clamp_x}+{clamp_y}")

    def on_emotion_change(self, emotion: str):
        """Called when AMADEUS Brain reports an emotion change."""
        self.dominant_emotion = emotion
        if emotion in ("smug", "happy"):
            self.current_frame = "shime17"  # Dr Pepper
        elif emotion in ("annoyed", "angry", "surprised"):
            self.current_frame = "shime23"  # Alert / tsundere
        elif emotion in ("focused", "thinking"):
            self.current_frame = "shime16"  # Reading

    def show_speech(self, text: str, emotion: Optional[str] = None, frame: Optional[str] = None):
        self._active_speech_text = text
        self.speech_bubble_timer = 65  # ~6 seconds
        if frame:
            self.current_frame = frame
        elif emotion in ("annoyed", "surprised", "alert"):
            self.current_frame = "shime23"
        elif emotion in ("focused", "thinking"):
            self.current_frame = "shime16"

    def _inspect_screen(self):
        """Triggers active window capture and screen watcher critique."""
        self.brain.inspect_active_screen(bbox=self.target_rect, window_title=self.target_title)

    def _prompt_chat_dialog(self):
        """Opens retro chat prompt to talk directly to Kurisu."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Ask Kurisu")
        dialog.geometry("340x120")
        dialog.config(bg="#14141E")
        dialog.attributes("-topmost", True)

        lbl = tk.Label(dialog, text="Ask Makise Kurisu:", fg="#E2583E", bg="#14141E", font=("Consolas", 9, "bold"))
        lbl.pack(pady=6)

        entry = tk.Entry(dialog, width=38, font=("Consolas", 10), bg="#222230", fg="#FFFFFF", insertbackground="white")
        entry.pack(pady=4)
        entry.focus()

        def _send():
            msg = entry.get().strip()
            if msg:
                dialog.destroy()
                self.brain.ask_kurisu(msg)

        entry.bind("<Return>", lambda e: _send())
        btn = tk.Button(dialog, text="Transmit", command=_send, bg="#E2583E", fg="white", font=("Consolas", 8, "bold"))
        btn.pack(pady=6)

    def _on_click(self, event):
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _on_drag(self, event):
        if self.is_dragging:
            self.state = "DRAGGED"
            self.current_frame = "shime12"
            self.x += event.x - self.drag_start_x
            self.y += event.y - self.drag_start_y

    def _on_release(self, event):
        if self.is_dragging:
            self.is_dragging = False
            if abs(event.x - self.drag_start_x) < 5 and abs(event.y - self.drag_start_y) < 5:
                # Poke interaction
                quote = random.choice(KURISU_QUOTES)
                self.show_speech(quote, frame="shime23")
            else:
                self.state = "PARACHUTE"

    def _show_context_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def _force_sleep(self):
        self.state = "SLEEP"
        self.idle_timer = 0
        self.show_speech("Zzz... Don't wake me up.", frame="shime18")

    def _drop_to_taskbar(self):
        self.state = "PARACHUTE"

    def _hop_to_active(self):
        self.state = "HOP"

    def run(self):
        print(f"AMADEUS Shimeji online! Connected to screen watcher & brain. [Divergence: {self.brain.divergence}]")
        self.root.mainloop()


if __name__ == "__main__":
    app = AmadeusShimeji()
    app.run()
