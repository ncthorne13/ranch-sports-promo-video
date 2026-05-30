#!/usr/bin/env python3
"""
The Ranch Sports - Promotional Video Generator
Generates a 25-second promotional video for theranchsports.com

Requirements:
    pip install Pillow numpy
    brew install ffmpeg   (macOS)

Usage:
    python3 generate_video.py

Output:
    ~/ranch_sports_video/ranch_sports_promo.mp4
"""

import os
import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Brand Colors ──────────────────────────────────────────────────────────────
NAVY     = (13,  27,  64)
RED      = (200, 30,  30)
GOLD     = (255, 180, 0)
WHITE    = (255, 255, 255)
BLACK    = (0,   0,   0)
DARK_RED = (160, 20,  20)
LT_NAVY  = (20,  40,  90)

# ── Video Settings ────────────────────────────────────────────────────────────
W, H   = 1280, 720
FPS    = 30
TOTAL  = 25
NFRAME = TOTAL * FPS

# ── Output ────────────────────────────────────────────────────────────────────
OUT_DIR    = os.path.expanduser("~/ranch_sports_video")
FRAMES_DIR = os.path.join(OUT_DIR, "frames")
OUT_MP4    = os.path.join(OUT_DIR, "ranch_sports_promo.mp4")

os.makedirs(FRAMES_DIR, exist_ok=True)


# ── Font helpers ──────────────────────────────────────────────────────────────
def get_font(size, bold=False):
    """Return a PIL font; falls back gracefully on any OS."""
    candidates = [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ── Easing ────────────────────────────────────────────────────────────────────
def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ── Drawing helpers ───────────────────────────────────────────────────────────
def centered_text(draw, img_size, text, y, font, color, shadow=True):
    W_img, _ = img_size
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W_img - tw) // 2
    if shadow:
        draw.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0, 140))
    draw.text((x, y), text, font=font, fill=color)
    return x, y

def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def alpha_text(img, text, cx_offset, y, font, color, alpha):
    """Render text with alpha over img (RGBA compositing)."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (img.width - tw) // 2 + cx_offset
    d.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, alpha // 2))
    d.text((x, y), text, font=font, fill=(*color, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def draw_diagonal_stripes(draw, stripe_color, width=80, gap=60, offset=0):
    """Draw subtle diagonal background stripes."""
    for i in range(-H, W + H, gap + width):
        pts = [
            (i + offset, 0),
            (i + width + offset, 0),
            (i + width - H + offset, H),
            (i - H + offset, H),
        ]
        draw.polygon(pts, fill=stripe_color)


# ── Scene 1: Intro — Logo Burst (0–4 s) ──────────────────────────────────────
def scene_intro(frame_idx):
    lt = frame_idx / FPS  # 0..4
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Background stripes
    stripe_offset = int(lt * 30)
    draw_diagonal_stripes(draw, LT_NAVY, width=50, gap=70, offset=stripe_offset)

    p = ease_out(min(lt / 1.5, 1.0))

    # Red accent bar
    bar_h = int(80 * p)
    draw.rectangle([(0, H // 2 - 70), (W, H // 2 - 70 + bar_h)], fill=RED)

    # Gold underline sweeps in
    ul_w = int(W * p)
    draw.rectangle([(W // 2 - ul_w // 2, H // 2 + 50),
                    (W // 2 + ul_w // 2, H // 2 + 60)], fill=GOLD)

    # Main title slides up
    slide = int((1 - p) * 130)
    font_title = get_font(100, bold=True)
    centered_text(draw, (W, H), "THE RANCH",  H // 2 - 100 + slide, font_title, WHITE)
    centered_text(draw, (W, H), "SPORTS",      H // 2 +  10 + slide, font_title, GOLD)

    # Tagline fades in
    if lt > 2.0:
        fa = min((lt - 2.0) / 1.5, 1.0)
        img = alpha_text(img, "\u26BE  Gear Up. Play Better.  \u26BE",
                         0, H // 2 + 145, get_font(38), WHITE, int(255 * fa))

    # "Tucson's #1 Baseball Store" badge
    if lt > 3.0:
        fa2 = min((lt - 3.0) / 0.8, 1.0)
        img = alpha_text(img, "Tucson's Premier Baseball & Softball Shop",
                         0, H - 60, get_font(26), GOLD, int(220 * fa2))

    return img


# ── Scene 2: Gear Showcase (4–9 s) ───────────────────────────────────────────
def scene_gear(frame_idx):
    lt = (frame_idx / FPS) - 4.0  # 0..5
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Gradient background
    arr = np.array(img)
    for y in range(H):
        arr[y, :] = lerp_color(NAVY, (18, 8, 48), y / H)
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)

    # Animated red diagonal accents
    for k, xo in enumerate([-160, 480, 1000]):
        shift = int(math.sin(lt * 2.5 + k * 1.3) * 18)
        c = RED if k % 2 == 0 else GOLD
        draw.polygon([
            (xo + shift,        0),
            (xo + 90 + shift,   0),
            (xo + 70 + shift,   H),
            (xo - 20 + shift,   H),
        ], fill=(*c, 180))

    # Section header
    centered_text(draw, (W, H), "SHOP PREMIUM GEAR",
                  35, get_font(44, bold=True), GOLD)
    draw.rectangle([(300, 95), (W - 300, 101)], fill=RED)

    # Gear items fly in one at a time
    items = [
        ("\U0001F3CF  BATS",     1.0,  160),
        ("\U0001F9E4  GLOVES",   2.0,  275),
        ("\u26D1\uFE0F  HELMETS", 3.0, 390),
        ("\U0001F45F  CLEATS",   4.0,  505),
    ]
    for label, delay, yp in items:
        if lt > delay:
            p2 = ease_out(min((lt - delay) / 0.55, 1.0))
            slide = int((1 - p2) * 320)
            # Card
            x1 = int(120 * (1 - p2))
            draw.rounded_rectangle(
                [(80 + x1 + slide, yp - 5), (W - 80 - x1 + slide, yp + 85)],
                radius=14, fill=(28, 50, 108), outline=GOLD, width=3)
            # Text
            font_it = get_font(50, bold=True)
            bbox = draw.textbbox((0, 0), label, font=font_it)
            tw = bbox[2] - bbox[0]
            draw.text(((W - tw) // 2 + slide, yp + 18), label,
                      font=font_it, fill=WHITE)

    if lt > 3.8:
        fa = ease_out(min((lt - 3.8) / 0.7, 1.0))
        img = alpha_text(img, "Everything Tucson Families Need",
                         0, H - 55, get_font(30), GOLD, int(240 * fa))
    return img


# ── Scene 3: Discount Hero (9–14 s) ──────────────────────────────────────────
def scene_discount(frame_idx):
    lt = (frame_idx / FPS) - 9.0  # 0..5
    img = Image.new("RGB", (W, H), DARK_RED)
    draw = ImageDraw.Draw(img)

    # Gradient red bg
    arr = np.array(img)
    for y in range(H):
        arr[y, :] = lerp_color(DARK_RED, RED, y / H)
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)

    # Gold corner triangles
    sz = 200
    draw.polygon([(0, 0), (sz, 0), (0, sz)], fill=GOLD)
    draw.polygon([(W, H), (W - sz, H), (W, H - sz)], fill=GOLD)

    # Navy divider
    draw.rectangle([(0, H // 2 - 4), (W, H // 2 + 4)], fill=NAVY)

    # Pulsing scale on "10% OFF"
    p3 = ease_out(min(lt / 1.0, 1.0))
    pulse = 1.0 + 0.04 * math.sin(lt * 3.5)
    font_huge = get_font(int(128 * pulse), bold=True)

    slide3 = int((1 - p3) * 100)
    centered_text(draw, (W, H), "10% OFF",
                  H // 2 - 140 + slide3, font_huge, WHITE)

    # Gold separator
    draw.rectangle([(200, H // 2 - 18), (W - 200, H // 2 - 11)], fill=GOLD)

    # No-tax line
    if lt > 1.0:
        p4 = ease_out(min((lt - 1.0) / 0.8, 1.0))
        ys = int((1 - p4) * 60)
        centered_text(draw, (W, H), "+ NO SALES TAX",
                      H // 2 + 20 + ys, get_font(58, bold=True), GOLD)

    if lt > 2.5:
        centered_text(draw, (W, H), "Save More on Every Order!",
                      H - 110, get_font(42, bold=True), WHITE)
    centered_text(draw, (W, H), "on all orders at theranchsports.com",
                  H - 60, get_font(22), (255, 215, 175))
    return img


# ── Scene 4: Code Reveal (14–19 s) ───────────────────────────────────────────
def scene_code(frame_idx):
    lt = (frame_idx / FPS) - 14.0  # 0..5
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Subtle glow bg
    arr = np.array(img)
    cx, cy = W // 2, H // 2
    for y in range(0, H, 2):
        for x in range(0, W, 4):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            glow = max(0.0, 1.0 - dist / (W * 0.55))
            arr[y:y+2, x:x+4] = lerp_color(NAVY, (30, 55, 20), glow * 0.45)
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)

    # Pulsing gold border
    pulse = 0.5 + 0.5 * math.sin(lt * 4.5)
    bw = int(5 + 5 * pulse)
    draw.rectangle([(18, 18), (W - 18, H - 18)], outline=GOLD, width=bw)

    # "USE CODE:" label
    p5 = ease_out(min(lt / 0.9, 1.0))
    img = alpha_text(img, "USE CODE AT CHECKOUT:",
                     0, H // 2 - 170, get_font(40), WHITE, int(255 * p5))

    # Red pill box (pulsing)
    box_pulse = 0.7 + 0.3 * math.sin(lt * 5)
    box_color = lerp_color(RED, DARK_RED, box_pulse)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([(190, H // 2 - 88), (W - 190, H // 2 + 82)],
                            radius=22, fill=box_color, outline=GOLD, width=5)

    # Code
    if lt > 0.4:
        p6 = ease_out(min((lt - 0.4) / 0.9, 1.0))
        img = alpha_text(img, "RANCH10",
                         0, H // 2 - 65, get_font(112, bold=True), GOLD, int(255 * p6))

    # Benefits reminder
    if lt > 2.0:
        img = alpha_text(img, "10% Off + Zero Sales Tax = Maximum Savings!",
                         0, H - 130, get_font(32), WHITE,
                         int(255 * ease_out(min((lt - 2.0) / 0.8, 1.0))))

    if lt > 3.0:
        img = alpha_text(img, "theranchsports.com",
                         0, H - 75, get_font(36, bold=True), GOLD,
                         int(255 * ease_out(min((lt - 3.0) / 0.7, 1.0))))
    return img


# ── Scene 5: CTA Closer (19–25 s) ────────────────────────────────────────────
def scene_cta(frame_idx):
    lt = (frame_idx / FPS) - 19.0  # 0..6
    fade_end = max(0.0, (lt - 5.0) / 1.0)

    img = Image.new("RGB", (W, H), NAVY)
    arr = np.array(img)
    for y in range(H):
        arr[y, :] = lerp_color(NAVY, (8, 15, 45), y / H)
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)

    # Animated diagonal stripes
    draw_diagonal_stripes(draw, LT_NAVY, width=40, gap=80, offset=int(lt * 20))

    # Gold + red bars
    bar_a = ease_out(min(lt / 0.9, 1.0))
    bh = int(14 * bar_a)
    draw.rectangle([(0, 0),      (W, bh)],      fill=GOLD)
    draw.rectangle([(0, H - bh), (W, H)],       fill=GOLD)
    draw.rectangle([(0, H // 2 - 3), (W, H // 2 + 3)], fill=RED)

    # Tagline
    p7 = ease_out(min(lt / 1.2, 1.0))
    s7 = int((1 - p7) * 80)
    font_tg = get_font(82, bold=True)
    centered_text(draw, (W, H), "Gear Up.",     H // 2 - 195 + s7, font_tg, WHITE)
    centered_text(draw, (W, H), "Play Better.", H // 2 -  95 + s7, font_tg, GOLD)

    # Website
    if lt > 1.5:
        img = alpha_text(img, "theranchsports.com",
                         0, H // 2 + 25, get_font(52, bold=True), WHITE,
                         int(255 * ease_out(min((lt - 1.5) / 1.0, 1.0))))

    # Code badge
    if lt > 2.5:
        pa = ease_out(min((lt - 2.5) / 0.8, 1.0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle(
            [(W // 2 - 285, H // 2 + 104),
             (W // 2 + 285, H // 2 + 170)],
            radius=14, fill=RED, outline=GOLD, width=3)
        img = alpha_text(img, "Code: RANCH10  —  10% Off + No Tax",
                         0, H // 2 + 115, get_font(40, bold=True), GOLD, int(255 * pa))

    if lt > 3.5:
        img = alpha_text(img,
                         "Serving Tucson Baseball & Softball Families",
                         0, H - 48, get_font(24), (170, 195, 255),
                         int(220 * ease_out(min((lt - 3.5) / 0.8, 1.0))))

    # Fade to black
    if fade_end > 0:
        black = Image.new("RGB", (W, H), BLACK)
        img = Image.blend(img, black, min(fade_end, 1.0))

    return img


# ── Main render loop ──────────────────────────────────────────────────────────
def make_frame(frame_idx):
    t = frame_idx / FPS
    if   t < 4.0:  return scene_intro(frame_idx)
    elif t < 9.0:  return scene_gear(frame_idx)
    elif t < 14.0: return scene_discount(frame_idx)
    elif t < 19.0: return scene_code(frame_idx)
    else:          return scene_cta(frame_idx)


if __name__ == "__main__":
    print(f"Rendering {NFRAME} frames at {FPS} fps ({TOTAL}s) …")
    for i in range(NFRAME):
        if i % FPS == 0:
            print(f"  Frame {i:4d} / {NFRAME}  ({i // FPS}s / {TOTAL}s)")
        frame = make_frame(i)
        frame.save(os.path.join(FRAMES_DIR, f"frame_{i:05d}.png"))

    print("\n\u2713 All frames rendered. Encoding with FFmpeg …")

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i",  os.path.join(FRAMES_DIR, "frame_%05d.png"),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf",    "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        OUT_MP4,
    ]
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("FFmpeg error:\n", result.stderr[-2000:])
        sys.exit(1)

    size_mb = os.path.getsize(OUT_MP4) / 1024 / 1024
    print(f"\n\u2713 Video saved: {OUT_MP4}  ({size_mb:.1f} MB)")
    print("\nDone! Open the file to preview your promo video.")
