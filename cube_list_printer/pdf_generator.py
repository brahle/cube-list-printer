import os
from typing import Any, Dict, List

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

TITLE_FONT_SIZE = 14
FONT_SIZE = 10
FONT_NAME = "Times-Roman"
TITLE_FONT_NAME = "Times-Bold"

SEPARATOR = " // "
SEPARATOR_PADDING = 2
BACKGROUND_OVERLAY_OPACITY = 0.7

INTERNAL_MARGIN = 7
TEXT_MARGIN_LEFT = 10
TEXT_MARGIN_TOP = 25
LINE_SPACING = FONT_SIZE + 2

COLS = 3
ROWS = 3
MARGIN_X = 25
MARGIN_Y = 25


def mm_to_points(mm_value: float) -> float:
    return mm_value * (72.0 / 25.4)


def load_mana_icons(symbol_map: Dict[str, str]) -> Dict[str, Image.Image]:
    """
    Load mana icons from the cached PNG files obtained from Scryfall symbology.
    symbol_map: { 'W': 'path/to/W.png', ... }

    Return a dict { 'W': PIL.Image, 'U': PIL.Image, ... }
    """
    icon_map = {}
    for sym, path in symbol_map.items():
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
            bg.alpha_composite(img)
            icon_map[sym] = bg.convert("RGBA")
    return icon_map


def draw_mana_cost_segment(
    c: canvas.Canvas, mana_cost: str, x: float, y: float, icon_map: Dict[str, Image.Image]
) -> float:
    if "{" in mana_cost:
        symbols = mana_cost.strip("{}").split("}{")
    else:
        symbols = []

    offset_x = 0.0
    icon_size = FONT_SIZE

    for sym in symbols:
        sym = sym.upper()
        # Some costs might be numeric like {2}, {3}, handle text fallback if no icon
        # Also consider hybrid/complex symbols might not be in icon_map, handle gracefully
        if sym in icon_map:
            img_reader = ImageReader(icon_map[sym])
            # Bottom align icon with text baseline. drawImage top aligns, so top = y - (icon_size - small_offset)
            # We'll use y - (icon_size - 1) to shift slightly
            c.drawImage(img_reader, x + offset_x, y - 1, width=icon_size, height=icon_size, mask="auto")
            offset_x += icon_size + SEPARATOR_PADDING
        else:
            # Draw text symbol if icon not found
            c.setFont(FONT_NAME, FONT_SIZE)
            text_width = c.stringWidth(sym, FONT_NAME, FONT_SIZE)
            c.drawString(x + offset_x, y, sym)
            offset_x += text_width + SEPARATOR_PADDING

    return offset_x - SEPARATOR_PADDING if offset_x > 0 else 0


def draw_mana_cost_full(
    c: canvas.Canvas, mana_cost: str, x: float, y: float, icon_map: Dict[str, Image.Image]
) -> float:
    parts = mana_cost.split(SEPARATOR)
    offset_x = 0.0
    c.setFont(FONT_NAME, FONT_SIZE)

    for i, part in enumerate(parts):
        offset_x += draw_mana_cost_segment(c, part, x + offset_x, y, icon_map)
        if i < len(parts) - 1:
            sep_width = c.stringWidth(SEPARATOR, FONT_NAME, FONT_SIZE)
            c.drawString(x + offset_x, y, SEPARATOR)
            offset_x += sep_width + SEPARATOR_PADDING

    return offset_x + 4


def draw_card_background(
    c: canvas.Canvas, bg_image_path: str, x: float, y: float, width: float, height: float
) -> None:
    c.drawImage(bg_image_path, x, y, width=width, height=height, mask="auto")

    c.saveState()
    c.setFillColor(colors.whitesmoke)
    c.setStrokeColor(colors.whitesmoke)
    c.setFillAlpha(BACKGROUND_OVERLAY_OPACITY)
    c.rect(
        x + INTERNAL_MARGIN,
        y + INTERNAL_MARGIN,
        width - 2 * INTERNAL_MARGIN,
        height - 2 * INTERNAL_MARGIN,
        fill=1,
        stroke=0,
    )
    c.restoreState()


def draw_card_title(c: canvas.Canvas, booster_id: str, x: float, y: float, width: float, height: float) -> None:
    c.setFont(TITLE_FONT_NAME, TITLE_FONT_SIZE)
    c.setFillColor(colors.black)
    booster_text_width = c.stringWidth(booster_id, TITLE_FONT_NAME, TITLE_FONT_SIZE)
    c.drawString(x + (width - booster_text_width) / 2, y + height - TEXT_MARGIN_TOP, booster_id)


def draw_card_list(
    c: canvas.Canvas,
    cards: List[Dict[str, Any]],
    icon_map: Dict[str, Image.Image],
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    c.setFont(FONT_NAME, FONT_SIZE)
    start_y = y + height - TEXT_MARGIN_TOP - 20
    current_y = start_y

    for card in cards:
        card_name = card.get("name", "Unknown Card")
        mana_cost = card.get("mana_cost", "")

        offset = 0.0
        c.drawString(x + TEXT_MARGIN_LEFT + offset, current_y, card_name)

        offset = c.stringWidth(card_name, FONT_NAME, FONT_SIZE) + 4
        if mana_cost:
            offset = draw_mana_cost_full(c, mana_cost, x + TEXT_MARGIN_LEFT + offset, current_y, icon_map)

        current_y -= LINE_SPACING


def create_card(
    c: canvas.Canvas,
    booster_id: str,
    cards: List[Dict[str, Any]],
    bg_image_path: str,
    x: float,
    y: float,
    width: float,
    height: float,
    icon_map: Dict[str, Image.Image],
) -> None:
    draw_card_background(c, bg_image_path, x, y, width, height)
    draw_card_title(c, booster_id, x, y, width, height)
    draw_card_list(c, cards, icon_map, x, y, width, height)


def get_background_image_path(most_valuable_card: Dict[str, Any]) -> str:
    bg_image_path = most_valuable_card.get("image_local_path", "")
    if not bg_image_path or not os.path.exists(bg_image_path):
        from cube_list_printer.image_handler import generate_placeholder_image

        s_id = most_valuable_card.get("scryfall_id", "unknown")
        bg_image_path = generate_placeholder_image("data/images", s_id)
    return bg_image_path


def generate_pdf(
    output_path: str,
    boosters: Dict[str, Any],
    icon_map: Dict[str, Image.Image],
    card_width_mm: float,
    card_height_mm: float,
) -> None:
    cw = mm_to_points(card_width_mm)
    ch = mm_to_points(card_height_mm)
    page_width, page_height = A4

    booster_ids = list(boosters.keys())
    c = canvas.Canvas(output_path, pagesize=A4)
    c.setTitle("Booster Cards")

    idx = 0
    while idx < len(booster_ids):
        for row in range(ROWS):
            for col in range(COLS):
                if idx >= len(booster_ids):
                    break
                booster_id = booster_ids[idx]
                booster_cards = boosters[booster_id]["cards"]

                if booster_cards:
                    most_valuable_card = max(booster_cards, key=lambda x: x.get("value", 0))
                    bg_image_path = get_background_image_path(most_valuable_card)

                    card_x = MARGIN_X + col * cw
                    card_y = page_height - MARGIN_Y - ch - row * ch

                    create_card(c, booster_id, booster_cards, bg_image_path, card_x, card_y, cw, ch, icon_map)

                idx += 1
        c.showPage()

    c.save()
