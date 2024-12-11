import os
from typing import Any, Dict, List

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

TITLE_FONT_SIZE = 14
FONT_SIZE = 10


def mm_to_points(mm_value: float) -> float:
    return mm_value * (72.0 / 25.4)


def load_mana_icons(icon_dir: str) -> Dict[str, Image.Image]:
    """
    Load mana icons, flatten them onto a white background.
    """
    icon_map = {}
    for mana_symbol in ["W", "U", "B", "R", "G", "C"]:
        path = os.path.join(icon_dir, f"{mana_symbol}.png")
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
            bg.alpha_composite(img)
            # Convert back to RGB
            final_img = bg.convert("RGB")
            icon_map[mana_symbol] = final_img
    return icon_map


def draw_mana_cost_segment(
    c: canvas.Canvas, mana_cost: str, x: float, y: float, icon_map: Dict[str, Image.Image]
) -> float:
    """
    Draw a single mana cost segment at baseline y.
    Icons and text bottom-align with baseline.
    """
    symbols = mana_cost.strip("{}").split("}{") if "{" in mana_cost else []
    offset_x = 0
    padding = 2
    icon_size = FONT_SIZE  # icon size in points

    for sym in symbols:
        sym = sym.upper()
        if sym in icon_map:
            # Use ImageReader for the PIL image
            img_reader = ImageReader(icon_map[sym])
            # Bottom align: baseline at y means top of icon at y - 1
            c.drawImage(img_reader, x + offset_x, y - 1, width=icon_size, height=icon_size, mask="auto")
            offset_x += icon_size + padding
        else:
            # Draw as text
            c.setFont("Helvetica", FONT_SIZE)
            text_width = c.stringWidth(sym, "Helvetica", FONT_SIZE)
            c.drawString(x + offset_x, y, sym)
            offset_x += text_width + padding
    return offset_x - padding


def draw_mana_cost_full(
    c: canvas.Canvas, mana_cost: str, x: float, y: float, icon_map: Dict[str, Image.Image]
) -> float:
    """
    Draw mana cost which may contain multiple parts separated by " // ".
    Each part is drawn with draw_mana_cost_segment, then ' // ' if needed.
    """
    parts = mana_cost.split(" // ")
    offset_x: float = 0
    c.setFont("Helvetica", FONT_SIZE)
    for i, part in enumerate(parts):
        offset_x += draw_mana_cost_segment(c, part, x + offset_x, y, icon_map)
        if i < len(parts) - 1:
            # Draw '//'
            sep = "//"
            sep_width = c.stringWidth(sep, "Helvetica", FONT_SIZE)
            c.drawString(x + offset_x, y, sep)
            offset_x += sep_width + 2
    return offset_x + 4


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
    # Slight internal margin
    image_margin = 7
    c.drawImage(
        bg_image_path,
        x,
        y,
        width=width,
        height=height,
        mask="auto",
    )

    # Internal margins for text
    text_margin_left = 10
    text_margin_top = 25

    # Semi-transparent overlay
    c.saveState()
    c.setFillColor(colors.whitesmoke)
    c.setStrokeColor(colors.whitesmoke)
    c.setFillAlpha(0.7)
    c.rect(x + image_margin, y + image_margin, width - 2 * image_margin, height - 2 * image_margin, fill=1, stroke=0)
    c.restoreState()

    # Booster Title: center horizontally
    c.setFont("Helvetica-Bold", TITLE_FONT_SIZE)
    c.setFillColor(colors.black)
    booster_text_width = c.stringWidth(booster_id, "Helvetica-Bold", TITLE_FONT_SIZE)
    c.drawString(x + (width - booster_text_width) / 2, y + height - text_margin_top, booster_id)

    # List cards
    c.setFont("Helvetica", FONT_SIZE)
    line_height = FONT_SIZE + 2
    text_start_y = y + height - text_margin_top - 20
    current_y = text_start_y

    for card in cards:
        card_name = card.get("name", "Unknown Card")
        mana_cost = card.get("mana_cost", "")

        offset = 0.0
        if mana_cost:
            offset = draw_mana_cost_full(c, mana_cost, x + text_margin_left, current_y, icon_map)

        c.drawString(x + text_margin_left + offset, current_y, card_name)
        current_y -= line_height


def generate_pdf(
    output_path: str,
    boosters: Dict[str, Any],
    icon_map: Dict[str, Image.Image],
    card_width_mm: float,
    card_height_mm: float,
) -> None:
    # Reduce card dimensions slightly to avoid clipping
    adjusted_card_width_mm = card_width_mm
    adjusted_card_height_mm = card_height_mm

    cw = mm_to_points(adjusted_card_width_mm)
    ch = mm_to_points(adjusted_card_height_mm)

    page_width, page_height = A4
    margin_x = 25
    margin_y = 25

    cols = 3
    rows = 3

    # x_spacing = (page_width - 2 * margin_x - cols * cw) / (cols - 1) if cols > 1 else 0
    # y_spacing = (page_height - 2 * margin_y - rows * ch) / (rows - 1) if rows > 1 else 0
    x_spacing = 0
    y_spacing = 0

    booster_ids = list(boosters.keys())

    c = canvas.Canvas(output_path, pagesize=A4)
    c.setTitle("Booster Cards")

    idx = 0
    while idx < len(booster_ids):
        for row in range(rows):
            for col in range(cols):
                if idx >= len(booster_ids):
                    break
                booster_id = booster_ids[idx]
                booster_cards = boosters[booster_id]["cards"]

                if booster_cards:
                    most_valuable_card = max(booster_cards, key=lambda x: x.get("value", 0))
                    bg_image_path = most_valuable_card.get("image_local_path", "")

                    if not bg_image_path or not os.path.exists(bg_image_path):
                        from cube_list_printer.image_handler import generate_placeholder_image

                        s_id = most_valuable_card.get("scryfall_id", "unknown")
                        bg_image_path = generate_placeholder_image("data/images", s_id)

                    card_x = margin_x + col * (cw + x_spacing)
                    card_y = page_height - margin_y - ch - row * (ch + y_spacing)

                    create_card(c, booster_id, booster_cards, bg_image_path, card_x, card_y, cw, ch, icon_map)
                idx += 1
        c.showPage()

    c.save()
