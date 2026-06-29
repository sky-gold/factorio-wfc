"""Export individual item icons from FactorioLab atlas to data/icons/."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DRAFT_DATA_DIR = PROJECT_ROOT / "factorio_wfc_draft" / "data"
DATA_JSON = DRAFT_DATA_DIR / "data.json"
ATLAS_PATH = DRAFT_DATA_DIR / "icons.webp"
OUTPUT_DIR = PROJECT_ROOT / "data" / "icons"

ICON_SIZE = 64
JPG_BACKGROUND = (48, 48, 48)


def _rgba_to_rgb(image: Image.Image) -> Image.Image:
    if image.mode == "RGB":
        return image
    background = Image.new("RGBA", image.size, (*JPG_BACKGROUND, 255))
    background.paste(image, mask=image.split()[3])
    return background.convert("RGB")


def export_icons() -> int:
    if not DATA_JSON.exists():
        raise FileNotFoundError(f"Missing icon metadata: {DATA_JSON}")
    if not ATLAS_PATH.exists():
        raise FileNotFoundError(f"Missing icon atlas: {ATLAS_PATH}")

    raw = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    icons = raw.get("icons", [])
    if not icons:
        raise ValueError("No icons entries in data.json")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    atlas = Image.open(ATLAS_PATH).convert("RGBA")
    written = 0
    for entry in icons:
        icon_id = entry["id"]
        x = int(entry["x"])
        y = int(entry["y"])
        crop = atlas.crop((x, y, x + ICON_SIZE, y + ICON_SIZE))
        rgb = _rgba_to_rgb(crop)
        rgb.save(OUTPUT_DIR / f"{icon_id}.jpg", format="JPEG", quality=95)
        written += 1

    return written


def main() -> int:
    try:
        count = export_icons()
    except (FileNotFoundError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1

    print(f"Wrote {count} icons to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
