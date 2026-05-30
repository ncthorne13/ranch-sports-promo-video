# The Ranch Sports — Promo Video Generator

Generates a **25-second** promotional MP4 video for [theranchsports.com](https://theranchsports.com).

## Brand Spec
| Element | Value |
|---------|-------|
| Colors | Deep Navy `#0D1B40`, Bright Red `#C81E1E`, Gold `#FFB400` |
| Tagline | *Gear Up. Play Better.* |
| Discount | `RANCH10` — 10% Off + No Sales Tax |
| Audience | Tucson baseball & softball families |

## Video Scenes
| Time | Scene |
|------|-------|
| 0–4 s | Logo burst — "THE RANCH SPORTS" on animated navy background |
| 4–9 s | Gear showcase — BATS, GLOVES, HELMETS, CLEATS cards fly in |
| 9–14 s | Discount hero — giant "10% OFF + NO SALES TAX" on red |
| 14–19 s | Code reveal — pulsing `RANCH10` box on navy |
| 19–25 s | CTA closer — tagline + website + code badge + fade to black |

## Requirements
```bash
brew install ffmpeg          # macOS
pip3 install Pillow numpy
```

## Usage
```bash
bash run.sh
# — or —
python3 generate_video.py
```

## Output
```
~/ranch_sports_video/ranch_sports_promo.mp4   (1280x720, 25 s, ~3 MB)
```
