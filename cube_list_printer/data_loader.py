import json
import logging
from typing import Any, Dict, Tuple

import pandas as pd


def load_data(csv_path: str, json_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    logging.info("Loading CSV and JSON data...")
    df = pd.read_csv(csv_path)

    with open(json_path, "r", encoding="utf-8") as f:
        scryfall_data = json.load(f)

    scryfall_map = {}
    for card in scryfall_data:
        c_id = card.get("id")
        if c_id:
            scryfall_map[c_id] = card
        else:
            logging.warning("Card in Scryfall data missing 'id' field.")

    return df, scryfall_map


def get_boosters_from_dataframe(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    boosters = {}
    for booster_id, grp in df.groupby("Binder Name"):
        cards = []
        for _, row in grp.iterrows():
            s_id = row.get("Scryfall ID")
            name = row.get("Name", "Unknown")
            if pd.isnull(s_id):
                logging.warning(f"Card '{name}' in booster '{booster_id}' missing Scryfall ID.")
                continue
            card_info = {"name": name, "scryfall_id": s_id}
            cards.append(card_info)
        boosters[booster_id] = {"cards": cards}
    return boosters


def enrich_boosters_with_scryfall_data(boosters: Dict[str, Any], scryfall_map: Dict[str, Any]) -> None:
    for booster_id, booster_data in boosters.items():
        for card in booster_data["cards"]:
            s_id = card["scryfall_id"]
            if s_id in scryfall_map:
                card_meta = scryfall_map[s_id]
                card["mana_cost"] = card_meta.get("mana_cost", "")
                card["image_uris"] = card_meta.get("image_uris", {})
                # Using usd for value, fallback to 0
                card["value"] = float(card_meta.get("usd", 0.0))
            else:
                logging.warning(f"Scryfall data not found for Scryfall ID: {s_id}")
                card["mana_cost"] = ""
                card["image_uris"] = {}
                card["value"] = 0.0
