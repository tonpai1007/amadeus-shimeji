# 🥼 AMADEUS Retro Pixel Shimeji (Lab Assistant Desktop Companion)

A native, ultra-lightweight Windows desktop companion that walks on your active window title bars (VS Code, Chrome, Terminal), sits down to read a science journal, drinks Dr Pepper, parachutes on window minimize, and connects to the AMADEUS Brain.

---

## ⚡ Performance & Resource Profile

| Metric | AMADEUS Shimeji | Old Electron / WebGL Live2D |
| :--- | :--- | :--- |
| **GPU Usage** | **0.0%** (Direct 32-bit GDI / Tkinter transparent blit) | 10–25% (Constant WebGL canvas 60 FPS) |
| **RAM Footprint** | **~12–15 MB** | 200–450 MB (Chromium + Node.js) |
| **Idle Power** | **Sleep mode (0 FPS / zero CPU wakeups)** | Continuous frame rendering & physics |
| **Format Standard** | Universal **Shimeji-ee** (`shime1.png` – `shime46.png`) | Proprietary Live2D Cubism runtime |

---

## 🚀 Quick Start

Run the Shimeji companion directly from your AMADEUS root:

```bash
python tools/shimeji/amadeus_shimeji.py
```

To re-generate or upscale the starter 32-bit retro pixel sprite set:
```bash
python tools/shimeji/sprite_generator.py
```

---

## 🎮 Desktop Behaviors & Controls

- **Climbs Active Window:** Follows the top title bar of whatever window you are focused on (VS Code, Chrome, etc.).
- **Window Hopping:** When you Alt+Tab or click a different window, Kurisu hops across the screen to land on the new window header.
- **Parachute on Minimize:** When you minimize or show desktop (`Win + D`), she deploys a lab-coat parachute and drifts gently down to sit on the Windows Taskbar.
- **Sleep & Read Mode:** When you are typing or idle, she sits on the window ledge, reads a science journal, or sips Dr Pepper.
- **Left Click:** Pokes Kurisu for a random tsundere quote or reaction speech bubble.
- **Click & Drag:** Pick her up and toss her anywhere on screen; she will parachute down to the nearest ledge.
- **Right Click Context Menu:**
  - 💬 *Ask Kurisu*
  - 😴 *Force Sleep (0% resource mode)*
  - 🪂 *Drop to Taskbar*
  - 🧗 *Hop to Active Window*
  - ❌ *Dismiss / Exit*

---

## 🎨 Dropping In Official / Custom Sprite Packs

The engine adheres to the universal **Shimeji-ee** standard. To replace or expand Kurisu's sprites:

Drop any `shime1.png` through `shime46.png` files directly into:
```text
tools/shimeji/sprites/
├── shime1.png   (Standing / idle on window title bar)
├── shime2.png   (Walk frame 1)
├── shime3.png   (Walk frame 2)
├── shime12.png  (Jump / Hop between windows)
├── shime13.png  (Parachute drift frame 1)
├── shime14.png  (Parachute drift frame 2)
├── shime15.png  (Sitting on window ledge)
├── shime16.png  (Reading science journal)
├── shime17.png  (Drinking Dr Pepper)
├── shime18.png  (Sleeping / napping)
└── shime23.png  (Surprised / Brain alert)
```

Compatible sprite sources:
1. **GitHub:** [`David131131/makise-kurisu-desktop-pet`](https://github.com/David131131/makise-kurisu-desktop-pet)
2. **The Spriters Resource:** PC / Computer $\rightarrow$ *Steins;Gate 8bit: Hen'i Kuukan no Octet* (MAGES / 5pb official retro rips).
3. **DeviantArt / Shimeji-ee:** Any community-made Makise Kurisu Shimeji pack.
