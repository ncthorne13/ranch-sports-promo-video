#!/bin/bash
# Quick launcher for the Ranch Sports promo video generator
set -e

echo "Installing Python dependencies ..."
pip3 install Pillow numpy --quiet

echo "Checking for ffmpeg ..."
if ! command -v ffmpeg &> /dev/null; then
    echo "ERROR: ffmpeg not found. Install it with: brew install ffmpeg"
    exit 1
fi

echo "Generating video ..."
python3 generate_video.py

echo ""
echo "Done! Video saved to: ~/ranch_sports_video/ranch_sports_promo.mp4"
open ~/ranch_sports_video/ranch_sports_promo.mp4 2>/dev/null || true
