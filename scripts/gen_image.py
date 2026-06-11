#!/usr/bin/env python3
"""Generate one image via Magnific Mystic from a prompt and save it. Reads ~/mars_lib/.env."""
import os
import sys

sys.path.insert(0, "/home/jetson1/mars_lib")

from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/mars_lib/.env"))

from mars.config import Settings
from mars.content import generate_image

s = Settings()
print("has_magnific_key:", bool(s.magnific_api_key))

prompt = sys.argv[1] if len(sys.argv) > 1 else (
    "A small friendly robot content creator taking photos at a busy tech hackathon, "
    "vibrant modern editorial illustration, energetic, no text or words"
)
print("prompt:", prompt)

img = generate_image(prompt, s)
if img:
    with open("/home/jetson1/mars_gen.jpg", "wb") as f:
        f.write(img)
    print("SAVED /home/jetson1/mars_gen.jpg", len(img), "bytes")
else:
    print("NO IMAGE (no key set, or generation failed/timed out)")
