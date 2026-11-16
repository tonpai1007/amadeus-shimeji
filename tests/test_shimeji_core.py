"""Unit tests for AMADEUS Shimeji M3-M4 features."""

from __future__ import annotations

import sys
from pathlib import Path

SHIMEJI_ROOT = Path(__file__).resolve().parents[1]
if str(SHIMEJI_ROOT) not in sys.path:
    sys.path.insert(0, str(SHIMEJI_ROOT))

from amadeus_shimeji import clamp_to_screen, detect_app_persona  # noqa: E402
from live2d_viewer import has_live2d_model  # noqa: E402


def test_clamp_to_screen_bounds():
    assert clamp_to_screen(-50, -20, 1920, 1080, 128, 128) == (0.0, 0.0)
    assert clamp_to_screen(2500, 1500, 1920, 1080, 128, 128) == (1792.0, 952.0)
    assert clamp_to_screen(500, 300, 1920, 1080, 128, 128) == (500.0, 300.0)


def test_detect_app_persona():
    assert detect_app_persona("main.py - Visual Studio Code")[0] == "ide"
    assert detect_app_persona("Windows PowerShell")[0] == "terminal"
    assert detect_app_persona("Daily Note - Obsidian")[0] == "obsidian"
    assert detect_app_persona("Docs - Google Chrome")[0] == "browser"
    assert detect_app_persona("Untitled - Notepad") is None


def test_has_live2d_model(tmp_path):
    assert has_live2d_model() is True
    assert has_live2d_model(tmp_path) is False
