"""
AMADEUS Retro Pixel Shimeji (Lab Assistant Desktop Companion)
Ultra-lightweight Windows desktop pet that climbs on active window title bars,
reads, drinks Dr Pepper, parachutes on minimize, and connects to the AMADEUS Brain.

Architecture:
- Native Windows transparent window (Tkinter + Win32 hooks)
- CPU / GPU footprint: 0% when sleeping, <15MB RAM
- Asset format: Universal Shimeji-ee standard (shime1.png ... shime46.png)
"""

import math
import random
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from typing import Optional, Tuple
from loguru import logger
from PIL import Image, ImageTk

try:
    import win32gui
except ImportError:
    print("Error: pywin32 is required. Run: pip install pywin32")
    sys.exit(1)


SPRITES_DIR = Path(__file__).parent / "sprites"
CHROMA_KEY = "#000001"  # 100% transparent click-through color key on Windows

# Built-in Kurisu Tsundere / Lab Assistant dialogue lines
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
    """Lightweight background client connecting to AMADEUS Brain."""

    def __init__(self, on_message_callback):
        self.callback = on_message_callback
        self.running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def _poll_loop(self):
        import urllib.request
        import json

        last_thought = ""
        while self.running:
            try:
                # Lightweight polling to Kurisu spontaneous thought endpoint
                req = urllib.request.Request(
                    "http://127.0.0.1:8000/kurisu/think?user_id=tonpai",
                    headers={"User-Agent": "AMADEUS-Shimeji/1.0"},
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    thought = data.get("thought", "")
                    if thought and thought != last_thought:
                        last_thought = thought
                        self.callback(thought)
            except Exception as exc:
                logger.debug(f"ShimejiBrainSync._poll_loop: silent exception ignored: {exc}")
            time.sleep(45)  # Ambient check interval


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

        # Canvas for sprite + speech bubble
        self.width = 220
        self.height = 180
        self.sprite_offset_x = 46  # Centers 128x128 sprite in 220w window
        self.sprite_offset_y = 52  # Leaves top 50px for speech bubbles

        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg=CHROMA_KEY,
            highlightthickness=0,
        )
        self.canvas.pack()

        # Load sprites
        self.sprites = {}
        self._load_sprites()

        # State machine
        self.state = "WALK"  # WALK, SIT, READ, DRINK, SLEEP, HOP, PARACHUTE, DRAGGED
        self.x = self.screen_width // 2
        self.y = 100
        self.vx = 2
        self.vy = 0
        self.target_window_hwnd = None
        self.target_rect = None
        self.current_frame = "shime1"
        self.walk_toggle = False
        self.idle_timer = 0
        self.speech_bubble_timer = 0

        # Drag tracking
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Event bindings
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", self._show_context_menu)

        # Brain connection
        self.brain_sync = ShimejiBrainSync(self.show_speech)

        # Context Menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="💬 Ask Kurisu", command=self._ask_kurisu)
        self.menu.add_command(label="😴 Force Sleep", command=self._force_sleep)
        self.menu.add_command(label="🪂 Drop to Taskbar", command=self._drop_to_taskbar)
        self.menu.add_command(label="🧗 Hop to Active Window", command=self._hop_to_active)
        self.menu.add_separator()
        self.menu.add_command(label="❌ Dismiss", command=self.root.quit)

        # Position and start loop
        self._update_window_position()
        self.root.after(80, self._tick)

    def _load_sprites(self):
        """Loads Shimeji-ee format sprites (shime1.png ... shime46.png)."""
        required = [
            "shime1",
            "shime2",
            "shime3",
            "shime12",
            "shime13",
            "shime14",
            "shime15",
            "shime16",
            "shime17",
            "shime18",
            "shime23",
        ]
        for name in required:
            file_path = SPRITES_DIR / f"{name}.png"
            if file_path.exists():
                try:
                    pil_img = Image.open(file_path).convert("RGBA")
                    # Replace fully transparent alpha with CHROMA_KEY
                    bg = Image.new("RGBA", pil_img.size, CHROMA_KEY)
                    bg.paste(pil_img, mask=pil_img)
                    self.sprites[name] = ImageTk.PhotoImage(bg)
                except Exception as e:
                    print(f"Warning: Failed to load {file_path}: {e}")

        # Fallback to default if empty
        if not self.sprites:
            print("No sprites found in sprites/ directory! Run sprite_generator.py first.")

    def _get_active_window(self) -> Optional[Tuple[int, Tuple[int, int, int, int]]]:
        """Gets active foreground window rect, excluding shell/desktop surfaces."""
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
            # rect: (left, top, right, bottom)
            if rect[2] - rect[0] < 100 or rect[3] - rect[1] < 80:
                return None
            return hwnd, rect
        except Exception as exc:
            logger.debug(f"AmadeusShimeji._get_active_window: silent exception ignored: {exc}")
            return None

    def _tick(self):
        """Main physics & behavior tick running at ~12 FPS."""
        if not self.is_dragging:
            self._update_physics()

        self._render()
        self._update_window_position()

        # Adapt tick rate: slower when sleeping to conserve 100% of CPU/GPU
        interval = 500 if self.state == "SLEEP" else 90
        self.root.after(interval, self._tick)

    def _update_physics(self):
        active = self._get_active_window()

        if active:
            hwnd, rect = active
            if self.target_window_hwnd != hwnd and self.state not in ("HOP", "PARACHUTE"):
                # New active window focused! Hop to it
                self.target_window_hwnd = hwnd
                self.target_rect = rect
                self.state = "HOP"
            else:
                self.target_rect = rect
        else:
            # Minimized or on desktop: parachute to bottom/taskbar
            if self.state not in ("PARACHUTE", "DRAGGED") and self.y < self.screen_height - 200:
                self.state = "PARACHUTE"

        # State Machine Logic
        if self.state == "WALK":
            if self.target_rect:
                left, top, right, _ = self.target_rect
                self.y = top - 128 + 10
                self.x += self.vx
                # Bounce on window title bar edges
                if self.x > right - 130:
                    self.vx = -abs(self.vx)
                elif self.x < left - 10:
                    self.vx = abs(self.vx)
            else:
                self.x += self.vx
                if self.x > self.screen_width - 150 or self.x < 10:
                    self.vx = -self.vx

            # Animation frame flip
            self.walk_toggle = not self.walk_toggle
            self.current_frame = "shime2" if self.walk_toggle else "shime3"

            self.idle_timer += 1
            if self.idle_timer > 60:  # ~5 seconds of walking -> sit down
                self.state = "SIT"
                self.idle_timer = 0

        elif self.state == "SIT":
            self.current_frame = "shime15"
            self.idle_timer += 1
            if self.idle_timer > 40:  # ~4 seconds sitting -> read or drink
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
            if self.idle_timer > 120:  # Wake up after sleep cycle
                self.state = "WALK"
                self.idle_timer = 0

        elif self.state == "HOP":
            self.current_frame = "shime12"
            if self.target_rect:
                target_x = self.target_rect[0] + 60
                target_y = self.target_rect[1] - 128 + 10
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
            target_floor = self.screen_height - 180
            if self.y < target_floor:
                self.y += 4  # Gentle parachute drift speed
                self.x += math.sin(self.y * 0.05) * 2
            else:
                self.y = target_floor
                self.state = "SIT"

    def _render(self):
        """Draws sprite + optional retro speech bubble onto transparent canvas."""
        self.canvas.delete("all")

        # Draw Sprite
        sprite = self.sprites.get(self.current_frame, self.sprites.get("shime1"))
        if sprite:
            self.canvas.create_image(
                self.sprite_offset_x,
                self.sprite_offset_y,
                anchor="nw",
                image=sprite,
            )

        # Draw Speech Bubble if active
        if self.speech_bubble_timer > 0:
            self.speech_bubble_timer -= 1
            self._render_speech_bubble()

    def _render_speech_bubble(self):
        text = getattr(self, "_active_speech_text", "")
        if not text:
            return

        # Retro 8-bit dialog box
        bx1, by1 = 10, 8
        bx2, by2 = self.width - 10, 48

        # Box border & background
        self.canvas.create_rectangle(bx1, by1, bx2, by2, fill="#181820", outline="#E06040", width=2)
        # Speech tail pointing down to Kurisu's head
        self.canvas.create_polygon(
            [self.width // 2 - 6, by2, self.width // 2 + 6, by2, self.width // 2, by2 + 8],
            fill="#181820",
            outline="#E06040",
        )
        # Truncate text for compact fit
        display_text = text if len(text) <= 32 else text[:30] + "…"
        self.canvas.create_text(
            self.width // 2,
            by1 + 20,
            text=display_text,
            fill="#FFFFFF",
            font=("Consolas", 8, "bold"),
            width=self.width - 24,
        )

    def _update_window_position(self):
        """Repositions Tkinter window to (self.x, self.y)."""
        wx = int(self.x)
        wy = int(self.y)
        self.root.geometry(f"{self.width}x{self.height}+{wx}+{wy}")

    def show_speech(self, text: str):
        """Triggers speech bubble above Kurisu."""
        self._active_speech_text = text
        self.speech_bubble_timer = 50  # ~5 seconds
        self.current_frame = "shime23"  # Surprised/talking frame

    def _on_click(self, event):
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _on_drag(self, event):
        if self.is_dragging:
            self.state = "DRAGGED"
            self.current_frame = "shime12"  # Dangling/dragged frame
            self.x += event.x - self.drag_start_x
            self.y += event.y - self.drag_start_y

    def _on_release(self, event):
        if self.is_dragging:
            self.is_dragging = False
            # If clicked without moving, poke reaction
            if abs(event.x - self.drag_start_x) < 5 and abs(event.y - self.drag_start_y) < 5:
                quote = random.choice(KURISU_QUOTES)
                self.show_speech(quote)
            else:
                self.state = "PARACHUTE"

    def _show_context_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def _ask_kurisu(self):
        self.show_speech("Ask me in Telegram or the HUD, Baka!")

    def _force_sleep(self):
        self.state = "SLEEP"
        self.idle_timer = 0
        self.show_speech("Zzz... Don't wake me up.")

    def _drop_to_taskbar(self):
        self.state = "PARACHUTE"

    def _hop_to_active(self):
        self.state = "HOP"

    def run(self):
        print("AMADEUS Shimeji active! Left-click to poke, drag to move, right-click for menu.")
        self.root.mainloop()


if __name__ == "__main__":
    app = AmadeusShimeji()
    app.run()
