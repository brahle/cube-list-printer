import os
import time
import logging
import requests
from typing import Dict
from PIL import Image
from io import BytesIO
import cairosvg

SYMBOL_API = "https://api.scryfall.com/symbology"

def fetch_symbols(symbol_cache_dir: str, fetch_delay: float = 0.2) -> Dict[str, str]:
    """
    Fetch all card symbols from Scryfall, cache their SVGs as PNGs, and return a mapping from symbol to PNG path.

    :param symbol_cache_dir: Directory to store cached symbol images.
    :param fetch_delay: Delay between fetches to be polite to the API.
    :return: A dictionary mapping mana symbol strings (e.g., 'W', 'U', 'B', 'W/U') to paths of the cached PNG files.
    """
    os.makedirs(symbol_cache_dir, exist_ok=True)
    logging.info("Fetching Scryfall symbology...")

    resp = requests.get(SYMBOL_API, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    symbol_map = {}
    for item in data.get("data", []):
        symbol = item.get("symbol", "")
        represents_mana = item.get("represents_mana", False)
        appears_in_cost = item.get("appears_in_mana_costs", False)
        svg_uri = item.get("svg_uri")

        # We only care about symbols that represent mana and appear in mana costs.
        if represents_mana and appears_in_cost and svg_uri:
            # Example symbol: "{W/U}" -> strip braces -> "W/U"
            original_symbol_key = symbol.strip("{}").upper()
            # Replace slashes with underscores for safe filenames
            sym_key = original_symbol_key.replace("/", "_")

            png_path = os.path.join(symbol_cache_dir, f"{sym_key}.png")
            if not os.path.exists(png_path):
                logging.info(f"Fetching symbol {symbol} from {svg_uri}")
                svg_resp = requests.get(svg_uri, timeout=10)
                svg_resp.raise_for_status()

                # Convert SVG to PNG
                png_data = cairosvg.svg2png(bytestring=svg_resp.content)
                pil_img = Image.open(BytesIO(png_data)).convert("RGBA")
                white_bg = Image.new("RGBA", pil_img.size, (255, 255, 255, 255))
                white_bg.alpha_composite(pil_img)
                white_bg = white_bg.convert("RGB")
                white_bg.save(png_path, "PNG")

                time.sleep(fetch_delay)  # Polite delay

            symbol_map[original_symbol_key] = png_path

    return symbol_map
