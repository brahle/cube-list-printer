import logging
import os
import time
from io import BytesIO
from typing import Dict

import requests
from PIL import Image


def fetch_image(
    scryfall_id: str,
    image_uris: Dict[str, str],
    cache_dir: str,
    delay: float = 1.0,
) -> str:
    os.makedirs(cache_dir, exist_ok=True)
    filename = os.path.join(cache_dir, f"{scryfall_id}.jpg")

    if os.path.exists(filename):
        return filename

    image_url = image_uris.get("large") or image_uris.get("normal")
    if not image_url:
        logging.warning(f"No image URIs for card {scryfall_id}, using placeholder.")
        return generate_placeholder_image(cache_dir, scryfall_id)

    time.sleep(delay)
    resp = requests.get(image_url, timeout=10)
    resp.raise_for_status()
    img = Image.open(BytesIO(resp.content))
    img.save(filename, format="JPEG")
    return filename


def generate_placeholder_image(cache_dir: str, scryfall_id: str) -> str:
    placeholder_path = os.path.join(cache_dir, f"{scryfall_id}_placeholder.png")
    if not os.path.exists(placeholder_path):
        img = Image.new("RGB", (480, 680), color="grey")
        img.save(placeholder_path, format="JPEG")
    return placeholder_path
