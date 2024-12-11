import unittest
import pandas as pd
from cube_list_printer.data_loader import (
    get_boosters_from_dataframe,
    enrich_boosters_with_scryfall_data,
)


class TestDataLoader(unittest.TestCase):
    def test_get_boosters_from_dataframe(self):
        data = {
            "Binder Name": ["Booster1", "Booster1", "Booster2"],
            "Name": ["Card A", "Card B", "Card C"],
            "Scryfall ID": ["idA", "idB", "idC"],
        }
        df = pd.DataFrame(data)
        boosters = get_boosters_from_dataframe(df)
        self.assertIn("Booster1", boosters)
        self.assertEqual(len(boosters["Booster1"]["cards"]), 2)
        self.assertEqual(boosters["Booster1"]["cards"][0]["name"], "Card A")

    def test_enrich_boosters_with_scryfall_data(self):
        boosters = {"Booster1": {"cards": [{"name": "Card A", "scryfall_id": "idA"}]}}
        scryfall_map = {
            "idA": {
                "id": "idA",
                "mana_cost": "{W}{U}",
                "image_uris": {"normal": "http://example.com/cardA.jpg"},
                "usd": "1.50",
            }
        }
        enrich_boosters_with_scryfall_data(boosters, scryfall_map)
        self.assertEqual(boosters["Booster1"]["cards"][0]["mana_cost"], "{W}{U}")
        self.assertEqual(boosters["Booster1"]["cards"][0]["value"], 1.5)


if __name__ == "__main__":
    unittest.main()
