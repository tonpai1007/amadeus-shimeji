"""
Retro Chibi Kurisu Sprite Generator
Generates authentic 32-bit style pixel art frames for AMADEUS Shimeji.
Resolution: 64x64 base, nearest-neighbor upscaled to 128x128.
Colors: Steins;Gate authentic GBA/DS palette.
"""

from pathlib import Path
from PIL import Image, ImageDraw

PALETTE = {
    "outline": (34, 24, 28, 255),
    "hair_dark": (128, 48, 40, 255),
    "hair_main": (184, 76, 60, 255),
    "hair_light": (220, 116, 96, 255),
    "skin_dark": (224, 180, 150, 255),
    "skin_main": (250, 224, 204, 255),
    "skin_blush": (240, 140, 140, 255),
    "eye_color": (80, 70, 140, 255),
    "eye_white": (245, 245, 250, 255),
    "coat_white": (240, 242, 245, 255),
    "coat_shadow": (195, 202, 212, 255),
    "shirt_white": (255, 255, 255, 255),
    "tie_red": (190, 30, 45, 255),
    "shorts_dark": (45, 45, 55, 255),
    "tights_dark": (60, 50, 60, 255),
    "boots_brown": (110, 65, 45, 255),
    "boots_dark": (70, 40, 30, 255),
    "dr_pepper_red": (150, 15, 30, 255),
    "dr_pepper_white": (240, 240, 240, 255),
    "book_green": (40, 110, 80, 255),
    "book_pages": (245, 240, 220, 255),
    "chute_cloth": (245, 245, 250, 255),
    "chute_lines": (160, 170, 185, 255),
}


def create_base_canvas():
    return Image.new("RGBA", (64, 64), (0, 0, 0, 0))


def draw_kurisu_head(draw, x_offset=0, y_offset=0, expression="neutral"):
    # Head base (Chibi 2.5 ratio: Head is roughly 22x18 pixels)
    hx = 21 + x_offset
    hy = 14 + y_offset

    # Hair Back
    draw.rectangle([hx - 4, hy + 2, hx + 24, hy + 22], fill=PALETTE["hair_dark"])

    # Face Skin
    draw.rectangle([hx, hy + 4, hx + 20, hy + 18], fill=PALETTE["skin_main"])
    draw.rectangle([hx + 1, hy + 18, hx + 19, hy + 19], fill=PALETTE["skin_main"])

    # Hair Bangs & Front
    draw.rectangle([hx - 2, hy, hx + 22, hy + 5], fill=PALETTE["hair_main"])
    draw.rectangle([hx - 3, hy + 3, hx + 3, hy + 16], fill=PALETTE["hair_main"])  # Left side lock
    draw.rectangle([hx + 17, hy + 3, hx + 23, hy + 16], fill=PALETTE["hair_main"])  # Right side lock
    draw.rectangle([hx + 6, hy + 4, hx + 8, hy + 9], fill=PALETTE["hair_main"])  # Center bang
    draw.rectangle([hx + 12, hy + 4, hx + 15, hy + 8], fill=PALETTE["hair_main"])  # Right bang

    # Hair Ahoge (Iconic top stray hair)
    draw.point((hx + 8, hy - 2), fill=PALETTE["hair_main"])
    draw.point((hx + 9, hy - 1), fill=PALETTE["hair_main"])
    draw.point((hx + 10, hy - 1), fill=PALETTE["hair_light"])

    # Eyes & Eyebrows
    if expression == "sleep":
        # Closed curved eyes ^ ^
        draw.line([(hx + 4, hy + 11), (hx + 7, hy + 10)], fill=PALETTE["outline"], width=1)
        draw.line([(hx + 7, hy + 10), (hx + 8, hy + 12)], fill=PALETTE["outline"], width=1)
        draw.line([(hx + 12, hy + 12), (hx + 13, hy + 10)], fill=PALETTE["outline"], width=1)
        draw.line([(hx + 13, hy + 10), (hx + 16, hy + 11)], fill=PALETTE["outline"], width=1)
    elif expression == "surprised":
        # Wide open eyes
        draw.rectangle([hx + 4, hy + 9, hx + 8, hy + 14], fill=PALETTE["eye_white"])
        draw.rectangle([hx + 12, hy + 9, hx + 16, hy + 14], fill=PALETTE["eye_white"])
        draw.rectangle([hx + 5, hy + 10, hx + 7, hy + 13], fill=PALETTE["eye_color"])
        draw.rectangle([hx + 13, hy + 10, hx + 15, hy + 13], fill=PALETTE["eye_color"])
        # Blush
        draw.rectangle([hx + 2, hy + 14, hx + 4, hy + 15], fill=PALETTE["skin_blush"])
        draw.rectangle([hx + 16, hy + 14, hx + 18, hy + 15], fill=PALETTE["skin_blush"])
    else:
        # Standard cute anime eyes
        draw.rectangle([hx + 4, hy + 10, hx + 8, hy + 14], fill=PALETTE["eye_white"])
        draw.rectangle([hx + 12, hy + 10, hx + 16, hy + 14], fill=PALETTE["eye_white"])
        draw.rectangle([hx + 5, hy + 10, hx + 7, hy + 13], fill=PALETTE["eye_color"])
        draw.rectangle([hx + 13, hy + 10, hx + 15, hy + 13], fill=PALETTE["eye_color"])
        draw.point((hx + 5, hy + 10), fill=(255, 255, 255, 255))  # Catchlight
        draw.point((hx + 13, hy + 10), fill=(255, 255, 255, 255))
        # Small blush dots
        draw.point((hx + 3, hy + 14), fill=PALETTE["skin_blush"])
        draw.point((hx + 17, hy + 14), fill=PALETTE["skin_blush"])


def draw_kurisu_body(draw, x_offset=0, y_offset=0, coat_flare=0):
    bx = 23 + x_offset
    by = 33 + y_offset

    # Shirt & Tie
    draw.rectangle([bx + 4, by, bx + 12, by + 10], fill=PALETTE["shirt_white"])
    # Loose Red Tie
    draw.line([(bx + 8, by + 1), (bx + 8, by + 9)], fill=PALETTE["tie_red"], width=2)

    # Open Lab Coat (Flaring out slightly)
    draw.rectangle([bx, by, bx + 4, by + 14], fill=PALETTE["coat_white"])
    draw.rectangle([bx + 12, by, bx + 16 + coat_flare, by + 14], fill=PALETTE["coat_white"])
    draw.line([(bx - 1, by + 4), (bx - 1, by + 14)], fill=PALETTE["coat_shadow"], width=1)
    draw.line([(bx + 16 + coat_flare, by + 4), (bx + 16 + coat_flare, by + 14)], fill=PALETTE["coat_shadow"], width=1)

    # Black Shorts
    draw.rectangle([bx + 5, by + 10, bx + 11, by + 14], fill=PALETTE["shorts_dark"])


def generate_standing_sprite():
    img = create_base_canvas()
    draw = ImageDraw.Draw(img)
    draw_kurisu_head(draw)
    draw_kurisu_body(draw)
    # Legs / Boots (standing straight)
    draw.rectangle([28, 48, 30, 56], fill=PALETTE["tights_dark"])
    draw.rectangle([33, 48, 35, 56], fill=PALETTE["tights_dark"])
    draw.rectangle([27, 56, 31, 60], fill=PALETTE["boots_brown"])
    draw.rectangle([32, 56, 36, 60], fill=PALETTE["boots_brown"])
    return img


def generate_walk_sprites():
    # Walk 1 (Left foot step)
    img1 = create_base_canvas()
    draw1 = ImageDraw.Draw(img1)
    draw_kurisu_head(draw1, y_offset=1)
    draw_kurisu_body(draw1, y_offset=1, coat_flare=1)
    draw1.rectangle([26, 49, 29, 56], fill=PALETTE["tights_dark"])
    draw1.rectangle([25, 56, 30, 60], fill=PALETTE["boots_brown"])  # Left foot forward
    draw1.rectangle([34, 49, 37, 55], fill=PALETTE["tights_dark"])
    draw1.rectangle([34, 55, 38, 59], fill=PALETTE["boots_brown"])  # Right foot back

    # Walk 2 (Right foot step)
    img2 = create_base_canvas()
    draw2 = ImageDraw.Draw(img2)
    draw_kurisu_head(draw2, y_offset=1)
    draw_kurisu_body(draw2, y_offset=1, coat_flare=-1)
    draw2.rectangle([27, 49, 30, 55], fill=PALETTE["tights_dark"])
    draw2.rectangle([26, 55, 30, 59], fill=PALETTE["boots_brown"])
    draw2.rectangle([33, 49, 36, 56], fill=PALETTE["tights_dark"])
    draw2.rectangle([33, 56, 38, 60], fill=PALETTE["boots_brown"])

    return img1, img2


def generate_sit_sprite():
    img = create_base_canvas()
    draw = ImageDraw.Draw(img)
    draw_kurisu_head(draw, y_offset=5)
    draw_kurisu_body(draw, y_offset=5)
    # Legs dangling down from the ledge
    draw.rectangle([28, 52, 31, 60], fill=PALETTE["tights_dark"])
    draw.rectangle([32, 52, 35, 60], fill=PALETTE["tights_dark"])
    draw.rectangle([28, 60, 32, 63], fill=PALETTE["boots_brown"])
    draw.rectangle([32, 60, 36, 63], fill=PALETTE["boots_brown"])
    return img


def generate_reading_sprite():
    img = generate_sit_sprite()
    draw = ImageDraw.Draw(img)
    # Holding Science Journal in front of chest
    draw.rectangle([27, 41, 37, 49], fill=PALETTE["book_green"])
    draw.rectangle([29, 43, 35, 47], fill=PALETTE["book_pages"])
    # Little reading glasses or head tilt
    draw.line([(28, 44), (34, 44)], fill=(120, 120, 120, 255), width=1)
    return img


def generate_dr_pepper_sprite():
    img = generate_sit_sprite()
    draw = ImageDraw.Draw(img)
    # Holding Red Dr Pepper Can
    draw.rectangle([37, 39, 42, 48], fill=PALETTE["dr_pepper_red"])
    draw.rectangle([38, 40, 41, 42], fill=PALETTE["dr_pepper_white"])
    # Arm holding it
    draw.line([(34, 42), (37, 43)], fill=PALETTE["coat_white"], width=2)
    return img


def generate_parachute_sprite():
    img = create_base_canvas()
    draw = ImageDraw.Draw(img)
    # Mini Lab-Coat Parachute Canopy above head
    draw.arc([14, 2, 50, 24], 180, 0, fill=PALETTE["chute_cloth"], width=6)
    draw.line([(18, 14), (32, 28)], fill=PALETTE["chute_lines"], width=1)
    draw.line([(46, 14), (32, 28)], fill=PALETTE["chute_lines"], width=1)
    # Floating body with arms up
    draw_kurisu_head(draw, y_offset=14, expression="surprised")
    draw_kurisu_body(draw, y_offset=14, coat_flare=3)
    # Legs drifting
    draw.rectangle([27, 61, 30, 63], fill=PALETTE["boots_brown"])
    draw.rectangle([33, 60, 36, 62], fill=PALETTE["boots_brown"])
    return img


def generate_surprised_sprite():
    img = create_base_canvas()
    draw = ImageDraw.Draw(img)
    draw_kurisu_head(draw, expression="surprised")
    draw_kurisu_body(draw, coat_flare=2)
    # Standing slightly startled
    draw.rectangle([27, 48, 30, 56], fill=PALETTE["tights_dark"])
    draw.rectangle([33, 48, 36, 56], fill=PALETTE["tights_dark"])
    draw.rectangle([26, 56, 30, 60], fill=PALETTE["boots_brown"])
    draw.rectangle([33, 56, 37, 60], fill=PALETTE["boots_brown"])
    return img


def generate_jump_sprite():
    img = create_base_canvas()
    draw = ImageDraw.Draw(img)
    draw_kurisu_head(draw, y_offset=-2)
    draw_kurisu_body(draw, y_offset=-2, coat_flare=2)
    # Legs tucked up in a hop
    draw.rectangle([28, 44, 31, 51], fill=PALETTE["tights_dark"])
    draw.rectangle([32, 44, 35, 51], fill=PALETTE["tights_dark"])
    draw.rectangle([27, 51, 31, 55], fill=PALETTE["boots_brown"])
    draw.rectangle([32, 51, 36, 55], fill=PALETTE["boots_brown"])
    return img


def build_all_sprites(output_dir: Path, scale=2):
    """Generates all Shimeji frames upscaled nearest-neighbor to crisp 128x128."""
    output_dir.mkdir(parents=True, exist_ok=True)

    walk1, walk2 = generate_walk_sprites()
    frames = {
        "shime1.png": generate_standing_sprite(),
        "shime2.png": walk1,
        "shime3.png": walk2,
        "shime12.png": generate_jump_sprite(),
        "shime13.png": generate_parachute_sprite(),
        "shime14.png": generate_parachute_sprite(),
        "shime15.png": generate_sit_sprite(),
        "shime16.png": generate_reading_sprite(),
        "shime17.png": generate_dr_pepper_sprite(),
        "shime18.png": generate_dr_pepper_sprite(),
        "shime23.png": generate_surprised_sprite(),
    }

    for name, img in frames.items():
        if scale > 1:
            # Nearest-neighbor upscale for crisp retro pixel art
            w, h = img.size
            img = img.resize((w * scale, h * scale), resample=Image.NEAREST)
        path = output_dir / name
        img.save(path)
        print(f"Generated: {path.name}")


if __name__ == "__main__":
    out = Path(__file__).parent / "sprites"
    build_all_sprites(out, scale=2)
    print("All starter Shimeji frames successfully created!")
