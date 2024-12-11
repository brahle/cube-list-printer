# Cube List Printer

**Cube List Printer** is a Python-based utility for generating PDF layouts of Magic: The Gathering booster pack representations from a CSV input. It integrates Scryfall’s bulk data and symbology APIs to fetch card details and mana symbols, rendering each booster’s cards along with their mana costs and a background image of their most valuable card.

This tool is especially useful for cube drafting events, mystery boosters, or custom sets where you want to visually represent the contents of boosters in a high-quality, printable format.

---

## Features

- **CSV Input**: Provide a CSV file listing boosters, each containing a set of 15 cards.
- **Scryfall Integration**:
  - Leverages a bulk JSON data file from Scryfall to retrieve card metadata (e.g., mana costs, image URIs, card values).
  - Uses the Scryfall Symbology API to fetch and cache mana symbols as PNG images.
- **On-the-Fly Image Fetching**: For any missing card images, the tool fetches them from Scryfall’s API (with configurable rate limiting).
- **Clean PDF Output**:
  - Each page displays a grid of boosters (default 3x3 layout).
  - Each booster shows a background image of its most valuable card.
  - All 15 cards are listed, alphabetically sorted by card name, alongside their mana costs.
  - Automatic handling of hybrid, phyrexian, and colorless mana icons.
  - Semi-transparent overlays improve legibility.
  - Professional typography and spacing ensure a clean, aesthetic layout.

- **Customizable Layout**: Adjust card sizes, margins, fonts, and icon directories via a configuration file.

---

## Requirements

- **Python 3.9+**
- **Dependencies** (listed in `requirements.txt`):
  - `pandas`
  - `requests`
  - `Pillow` (PIL)
  - `PyYAML`
  - `reportlab`
  - `pytest` (for tests)
  - `cairosvg` (for SVG to PNG conversion of mana symbols)

Ensure you have `cairosvg` installed so that SVG mana symbols are correctly converted.

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/cube_list_printer.git
   cd cube_list_printer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare Data**:
   - Place your `boosters.csv` file in a data directory (e.g., `data/mystery_booster_cube.csv`).
   - Obtain a Scryfall bulk data file (JSON) and place it under the `data` directory. Update `config/settings.yaml` with the correct paths.

4. **Configuration**:
   - Check and edit `config/settings.yaml` to set paths and parameters for:
     - CSV and bulk data file paths
     - Image cache directory
     - Symbol cache directory
     - Output PDF name and dimensions
     - Fetch delays to respect Scryfall’s rate limits

---

## Usage

Generate the PDF:
```bash
python cube_list_printer/main.py data/mystery_booster_cube.csv
```

If no CSV file is passed as an argument, it will use the default specified in `settings.yaml`.

On successful completion, a PDF file (e.g., `BoosterCards.pdf`) will be created, containing your arranged booster pages.

---

## Testing

Basic tests are available in the `tests/` directory. You can run them with:
```bash
pytest
```

This will check core functions like data loading, image handling, and PDF generation for basic correctness.

---

## Customization

You can customize various aspects by editing `config/settings.yaml`:

- **Layout**:
  Adjust card width/height in millimeters, margins, and font sizes.

- **Symbol Fetch Delay**:
  Control the delay between Scryfall API requests to avoid rate limiting.

- **Hybrid Mana & Special Costs**:
  The tool automatically handles symbols like `{W/U}` by sanitizing and caching them. No extra steps required.

---

## Known Limitations & Future Improvements

- **Transparency of Icons**:
  Icons are currently composited against a white background to avoid rendering issues. Full alpha transparency is limited by PDF rendering.

- **Performance**:
  For very large sets of boosters, consider pre-fetching images and symbols to speed up generation.

- **Further Custom Layout Options**:
  Future versions may allow more complex page layouts and styles.

---

## Contributing

Contributions are welcome!
- Fork the repository
- Create a new feature branch
- Submit a pull request

Please ensure code is well-documented, tested, and follows Pythonic best practices.

---

## License

This project is licensed under the Unlicense License. See the [LICENSE](LICENSE) file for details.

---

**Cube List Printer** brings automation and professional polish to printing custom booster sets, making your cube drafts more visually appealing and streamlined. Enjoy a smooth, ready-to-print PDF that showcases your curated Magic: The Gathering experience.
