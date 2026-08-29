"""Measure how bright the light-mode wallpapers actually are.

The showcase panels are near-white (each palette's light `background`), so if
the wallpaper behind them is mid-grey the composition reads muddy rather than
light. This compares each light wallpaper's mean luminance against the panel
colour it has to sit behind.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent

VARIANTS = {
    "blade-runner": ("", ""),
    "crow": ("crow", "crow-"),
    "amelie": ("amelie", "amelie-"),
    "tron": ("tron", "tron-"),
    "dark-city": ("dark-city", "dark-city-"),
    "fifth-element": ("fifth-element", "fifth-element-"),
    "grand-budapest": ("grand-budapest", "grand-budapest-"),
    "evangelion": ("evangelion", "evangelion-"),
    "matrix": ("matrix", "matrix-"),
    "solaris": ("solaris", "solaris-"),
    "suspiria": ("suspiria", "suspiria-"),
    "akira": ("akira", "akira-"),
    "dune": ("dune", "dune-"),
}


def _lin(c):
    c = c / 255.0
    return np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def img_lum(path):
    im = Image.open(path).convert("RGB")
    im.thumbnail((400, 400))
    a = np.asarray(im).astype(np.float32)
    lin = _lin(a)
    return float((0.2126 * lin[:, :, 0] + 0.7152 * lin[:, :, 1]
                  + 0.0722 * lin[:, :, 2]).mean())


def hex_lum(hx):
    hx = hx.lstrip("#")
    v = np.array([int(hx[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)
    lin = _lin(v)
    return float(0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2])


print(f"{'variant':16s} {'mode':6s} {'wall lum':>9s} {'panel lum':>10s} "
      f"{'gap':>7s}  reads as")
for tag, (wdir, stem) in VARIANTS.items():
    for mode in ("light", "dark"):
        wall = (ROOT / "wallpapers" / wdir / mode / "4k.png") if wdir else \
               (ROOT / "wallpapers" / mode / "4k.png")
        pal = json.loads((ROOT / "palettes" / f"{stem}{mode}.json").read_text())
        bg = pal.get("background") or pal["bg"]
        wl, pl = img_lum(wall), hex_lum(bg)
        gap = pl - wl
        if mode == "light":
            verdict = ("panel floats on grey" if gap > 0.35 else
                       "close enough" if gap > 0.15 else "cohesive")
        else:
            verdict = "ok (dark)"
        print(f"{tag:16s} {mode:6s} {wl:9.3f} {pl:10.3f} {gap:7.3f}  {verdict}")
