"""
Live2D Full-Model Pop-Out Viewer for AMADEUS Shimeji (M3).
Serves assets/live2d/kurisu/ on an ephemeral localhost HTTP port and opens a
lightweight pywebview window only on demand (0% GPU when closed).
"""

from __future__ import annotations

import functools
import http.server
import socketserver
import subprocess
import sys
import threading
from pathlib import Path

from loguru import logger

LIVE2D_DIR = Path(__file__).parent / "assets" / "live2d" / "kurisu"
MODEL_JSON_NAME = "Kurisu.model3.json"

_VIEWER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>AMADEUS Kurisu Live2D</title>
<style>
  html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #14141E;
    color: #E8E6E3;
    font-family: Consolas, monospace;
  }
  #status {
    position: absolute;
    top: 8px;
    left: 10px;
    font-size: 11px;
    color: #FFB347;
    z-index: 10;
    background: rgba(20, 20, 30, 0.75);
    padding: 3px 8px;
    border-radius: 4px;
    pointer-events: none;
  }
  #controls {
    position: absolute;
    bottom: 8px;
    left: 10px;
    font-size: 10px;
    color: #888;
    z-index: 10;
    background: rgba(20, 20, 30, 0.6);
    padding: 4px 8px;
    border-radius: 4px;
    pointer-events: none;
    border: 1px solid #333;
  }
  canvas {
    display: block;
    width: 100%;
    height: 100%;
  }
</style>
<script src="https://cdn.jsdelivr.net/npm/pixi.js@6.5.10/dist/browser/pixi.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/live2dcubismcore@1.0.2/live2dcubismcore.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/pixi-live2d-display@0.4.0/dist/cubism4.min.js"></script>
</head>
<body>
<div id="status">Loading Kurisu Live2D...</div>
<div id="controls">Click Kurisu · 1-8 Expressions · Right-click menu</div>
<canvas id="stage"></canvas>
<script>
(async function () {
  const statusEl = document.getElementById("status");
  try {
    if (!window.PIXI || !PIXI.live2d || !window.Live2DCubismCore) {
      statusEl.textContent = "Live2D web runtime offline (check internet or use Brain HUD).";
      return;
    }
    const app = new PIXI.Application({
      view: document.getElementById("stage"),
      autoStart: true,
      resizeTo: window,
      backgroundAlpha: 0,
    });
    const model = await PIXI.live2d.Live2DModel.from("/Kurisu.model3.json");
    app.stage.addChild(model);
    function fitModel() {
      const scale = Math.min(window.innerWidth / model.width, window.innerHeight / model.height) * 0.92;
      model.scale.set(scale);
      model.anchor.set(0.5, 0.5);
      model.x = window.innerWidth / 2;
      model.y = window.innerHeight / 2 + 20;
    }
    fitModel();
    window.addEventListener("resize", fitModel);
    const MOTIONS = [
      "TapBody",
      "58Loop",
      "haru_g_idle",
      "mtn_07",
      "Out From Camera",
      "xhiyori_m03",
    ];
    const EXPRESSIONS = [
      "Stanby Smile",
      "Stanby Angry",
      "Stanby Surprised",
      "Stanby Sad",
      "Stanby Scared",
      "Blush 1",
      "Blush 2",
      "Arm Change",
    ];
    let motionIdx = 0;
    let currentMotion = null;

    function fitModel() {
      const scale = Math.min(window.innerWidth / model.width, window.innerHeight / model.height) * 0.92;
      model.scale.set(scale);
      model.anchor.set(0.5, 0.5);
      model.x = window.innerWidth / 2;
      model.y = window.innerHeight / 2 + 20;
    }
    fitModel();
    window.addEventListener("resize", fitModel);

    model.on("hit", () => {
      motionIdx = (motionIdx + 1) % MOTIONS.length;
      const m = MOTIONS[motionIdx];
      if (currentMotion) currentMotion.stop();
      currentMotion = model.motion(m);
      statusEl.textContent = "Motion: " + m;
      statusEl.style.opacity = "1";
      setTimeout(() => { statusEl.style.opacity = "0.35"; }, 2500);
    });

    window.addEventListener("keydown", (e) => {
      const key = e.key;
      if (key >= "1" && key <= "8") {
        const idx = parseInt(key) - 1;
        const exp = EXPRESSIONS[idx];
        if (exp) {
          model.expression(exp);
          statusEl.textContent = "Expression: " + exp;
          statusEl.style.opacity = "1";
          setTimeout(() => { statusEl.style.opacity = "0.35"; }, 2500);
        }
      }
    });

    const canvas = document.getElementById("stage");
    const menu = document.createElement("div");
    menu.style.position = "absolute";
    menu.style.display = "none";
    menu.style.zIndex = "100";
    menu.style.background = "#14141E";
    menu.style.border = "1px solid #FFB347";
    menu.style.color = "#FFB347";
    menu.style.fontFamily = "Consolas, monospace";
    menu.style.fontSize = "11px";
    menu.style.padding = "4px";
    menu.style.borderRadius = "4px";
    menu.style.minWidth = "140px";
    document.body.appendChild(menu);

    const motionsHtml = MOTIONS.map((m, i) =>
      "<div style=\"padding:2px 8px; cursor:pointer; border-bottom:1px solid #222;\" onclick=\"setMotion('" + m + "')\">" + (i+1) + ". " + m + "</div>"
    ).join("");
    const exprsHtml = EXPRESSIONS.map((e, i) =>
      "<div style=\"padding:2px 8px; cursor:pointer;\" onclick=\"setExpression('" + e + "')\">" + (i+1) + ". " + e + "</div>"
    ).join("");

    menu.innerHTML = "<div style=\"padding:4px 8px; font-weight:bold; border-bottom:1px solid #333;\">Kurisu Live2D</div><div style=\"font-size:9px; color:#666; padding:2px 8px;\">Motions:</div>" + motionsHtml + "<div style=\"font-size:9px; color:#666; padding:2px 8px;\">Expressions:</div>" + exprsHtml + "<div style=\"padding:4px 8px; font-size:9px; color:#888;\">Click outside to close</div>";

    window.setMotion = (name) => {
      if (currentMotion) currentMotion.stop();
      currentMotion = model.motion(name);
      statusEl.textContent = "Motion: " + name;
      statusEl.style.opacity = "1";
      menu.style.display = "none";
    };

    window.setExpression = (name) => {
      model.expression(name);
      statusEl.textContent = "Expression: " + name;
      statusEl.style.opacity = "1";
      menu.style.display = "none";
    };

    canvas.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      const rect = canvas.getBoundingClientRect();
      menu.style.left = (e.clientX - rect.left) + "px";
      menu.style.top = (e.clientY - rect.top) + "px";
      menu.style.display = "block";
    });

    document.addEventListener("click", () => {
      menu.style.display = "none";
    });

    statusEl.textContent = "Kurisu Live2D Online";
    setTimeout(() => { statusEl.style.opacity = "0.35"; }, 2500);
  } catch (err) {
    statusEl.textContent = "Live2D load error: " + (err && err.message ? err.message : String(err));
  }
})();
</script>
</body>
</html>
"""


def has_live2d_model(model_dir: Path = LIVE2D_DIR) -> bool:
    """Return True if the Kurisu Live2D model3.json asset exists on disk."""
    return (model_dir / MODEL_JSON_NAME).is_file()


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = _VIEWER_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, format, *args):
        return


def launch_live2d_process() -> subprocess.Popen | None:
    """Spawn this module as a standalone process so pywebview runs on its own main thread."""
    if not has_live2d_model():
        logger.warning(f"Live2D model not found at {LIVE2D_DIR / MODEL_JSON_NAME}")
        return None
    return subprocess.Popen([sys.executable, str(Path(__file__).resolve())])


def main() -> int:
    if not has_live2d_model():
        print(f"Live2D model missing: {LIVE2D_DIR / MODEL_JSON_NAME}")
        return 1

    import webview

    handler = functools.partial(_QuietHandler, directory=str(LIVE2D_DIR))
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            webview.create_window(
                "AMADEUS Kurisu Live2D",
                f"http://127.0.0.1:{port}/index.html",
                width=420,
                height=560,
                on_top=True,
            )
            webview.start()
        finally:
            httpd.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
