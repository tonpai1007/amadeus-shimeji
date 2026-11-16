"""Debug script to test Live2D viewer components"""
import sys
sys.path.insert(0, 'C:\\amadeus-shimeji')

# Test 1: Check model files exist
from pathlib import Path
model_dir = Path('C:\\amadeus-shimeji\\assets\\live2d\\kurisu')
print("=== Model Files ===")
for f in model_dir.iterdir():
    print(f"  {f.name}: {f.stat().st_size} bytes")

# Test 2: Check webview backend
print("\n=== WebView Backend ===")
try:
    import webview
    print(f"  pywebview version: {webview.__version__}")
    print(f"  GUI: {webview.GUI}")
except Exception as e:
    print(f"  pywebview import failed: {e}")

# Test 3: Check CDN URLs
print("\n=== CDN URLs ===")
import urllib.request
urls = [
    ('pixi.js', 'https://cdn.jsdelivr.net/npm/pixi.js@6.5.10/dist/browser/pixi.min.js'),
    ('cubismcore', 'https://cdn.jsdelivr.net/npm/live2dcubismcore@1.0.2/live2dcubismcore.min.js'),
    ('pixi-live2d-display', 'https://cdn.jsdelivr.net/npm/pixi-live2d-display@0.4.0/dist/cubism4.min.js'),
]
for name, url in urls:
    try:
        r = urllib.request.urlopen(url, timeout=5)
        data = r.read()
        print(f"  {name}: OK ({len(data)} bytes)")
    except Exception as e:
        print(f"  {name}: FAILED ({e})")

# Test 4: Check model JSON references
print("\n=== Model JSON ===")
import json
model_json_path = model_dir / "Kurisu.model3.json"
with open(model_json_path) as f:
    model_data = json.load(f)
print(f"  Moc file: {model_data['FileReferences']['Moc']}")
print(f"  Textures: {model_data['FileReferences']['Textures']}")
print(f"  Physics: {model_data['FileReferences']['Physics']}")
print(f"  DisplayInfo: {model_data['FileReferences']['DisplayInfo']}")

# Test 5: Check texture file
texture_path = model_dir / "Kurisu.4096" / "texture_00.png"
print(f"\n  Texture exists: {texture_path.exists()}, size: {texture_path.stat().st_size if texture_path.exists() else 'N/A'}")

print("\n=== All checks done ===")
