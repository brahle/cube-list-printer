import logging
import sys

import yaml

from cube_list_printer.data_loader import enrich_boosters_with_scryfall_data, get_boosters_from_dataframe, load_data
from cube_list_printer.image_handler import fetch_image, generate_placeholder_image
from cube_list_printer.pdf_generator import generate_pdf, load_mana_icons

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")


def main():
    # Load config
    with open("config/settings.yaml", "r") as f:
        config = yaml.safe_load(f)

    # If CSV passed via command line, use it; otherwise use config file path
    csv_path = sys.argv[1] if len(sys.argv) > 1 else config["paths"]["csv_file"]
    json_path = config["paths"]["scryfall_bulk"]
    image_cache_dir = config["paths"]["image_cache_dir"]
    icon_dir = config["paths"]["mana_icons_dir"]
    output_pdf = config["paths"]["output_pdf"]

    delay = config["fetch_delay"]
    card_width_mm = config["card_width_mm"]
    card_height_mm = config["card_height_mm"]

    # Load data
    try:
        df, scryfall_map = load_data(csv_path, json_path)
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        sys.exit(1)

    boosters = get_boosters_from_dataframe(df)
    enrich_boosters_with_scryfall_data(boosters, scryfall_map)

    # Sort each booster's cards alphabetically by card name
    for booster_id, data in boosters.items():
        data["cards"].sort(key=lambda c: c["name"].lower())

    # Fetch images for each booster's most valuable card
    for booster_id, data in boosters.items():
        cards = data["cards"]
        if not cards:
            logging.warning(f"Booster '{booster_id}' has no cards.")
            continue
        most_valuable = max(cards, key=lambda x: x.get("value", 0))

        s_id = most_valuable["scryfall_id"]
        image_uris = most_valuable.get("image_uris", {})
        try:
            local_path = fetch_image(s_id, image_uris, image_cache_dir, delay)
            most_valuable["image_local_path"] = local_path
        except Exception as e:
            logging.error(f"Failed to fetch image for card {most_valuable['name']} (Booster {booster_id}): {e}")
            most_valuable["image_local_path"] = generate_placeholder_image(image_cache_dir, s_id)

    # Load mana icons
    icon_map = load_mana_icons(icon_dir)

    # Generate PDF
    try:
        generate_pdf(output_pdf, boosters, icon_map, card_width_mm, card_height_mm)
        logging.info(f"PDF successfully created: {output_pdf}")
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
