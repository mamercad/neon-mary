#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import json

ROOT = Path(__file__).resolve().parent
expected = {"4k": (3840, 2160), "wqhd": (2560, 1440), "qhd": (1920, 1080), "16-10": (2560, 1600), "3-2": (2160, 1440), "4-3": (2048, 1536), "1-1": (2048, 2048), "9-16": (1440, 2560)}
for mode in ("dark", "light"):
    palette = json.loads((ROOT / "palettes" / f"crow-{mode}.json").read_text())
    assert palette["mode"] == mode
    for name, size in expected.items():
        for base in (ROOT / "wallpapers" / "crow" / mode, ROOT / "omarchy" / "themes" / f"neon-mary-crow-{mode}" / "backgrounds"):
            path = base / f"{name}.png"
            assert path.exists(), path
            with Image.open(path) as image:
                assert image.size == size, (path, image.size, size)
    assert (ROOT / "hermes" / "skins" / f"neon-mary-crow-{mode}.yaml").exists()
print("validated: Neon Mary The Crow (1994) dark/light palettes, 16 wallpapers, Omarchy packages, and Hermes skins")
