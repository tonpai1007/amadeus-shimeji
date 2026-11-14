"""
Asset Pack Installer for AMADEUS Shimeji
Swaps or installs archived sprite packs into tools/shimeji/sprites/.
"""

import argparse
from pathlib import Path
from PIL import Image

ARCHIVE_DIR = Path(__file__).parent
SPRITES_DIR = ARCHIVE_DIR.parent.parent / "sprites"


def install_david_pack():
    david_dir = ARCHIVE_DIR / "david131131_kurisu"
    pet_v2 = david_dir / "kurisu-pet-v2.png"
    pat = david_dir / "kurisu-pat.png"

    if not pet_v2.exists():
        print(f"Error: {pet_v2} not found.")
        return

    SPRITES_DIR.mkdir(parents=True, exist_ok=True)

    # Resize cleanly to 128x128
    im_idle = Image.open(pet_v2).convert("RGBA")
    im_idle.thumbnail((128, 128), Image.Resampling.LANCZOS)
    target_idle = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    offset_x = (128 - im_idle.width) // 2
    offset_y = 128 - im_idle.height
    target_idle.paste(im_idle, (offset_x, offset_y))
    target_idle.save(SPRITES_DIR / "shime1.png")
    target_idle.save(SPRITES_DIR / "shime2.png")
    target_idle.save(SPRITES_DIR / "shime3.png")

    if pat.exists():
        im_pat = Image.open(pat).convert("RGBA")
        im_pat.thumbnail((128, 128), Image.Resampling.LANCZOS)
        target_pat = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        target_pat.paste(im_pat, ((128 - im_pat.width) // 2, 128 - im_pat.height))
        target_pat.save(SPRITES_DIR / "shime23.png")

    print("✅ Installed David131131 Kurisu chibi pack into tools/shimeji/sprites/!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install Shimeji asset pack")
    parser.add_argument("--pack", choices=["david", "octet"], default="david")
    args = parser.parse_args()

    if args.pack == "david":
        install_david_pack()
