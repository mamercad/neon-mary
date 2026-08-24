"""Survey the Neon Mary palette landscape: how dark, how warm, how saturated.

Answers "what's missing?" with numbers instead of vibes. For each variant we
report background luminance, the mean saturation of the 6 accent slots, and
the warm/cool balance of those accents (circular mean hue).
"""
import colorsys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
import math


def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def lum(hx):
    hx = hx.lstrip("#")
    r, g, b = (int(hx[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def hsv(hx):
    hx = hx.lstrip("#")
    r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return colorsys.rgb_to_hsv(r, g, b)


def warmth(hues, sats):
    """Circular mean hue, saturation-weighted. 0-60 or 330-360 = warm."""
    x = sum(math.cos(math.radians(h * 360)) * s for h, s in zip(hues, sats))
    y = sum(math.sin(math.radians(h * 360)) * s for h, s in zip(hues, sats))
    return math.degrees(math.atan2(y, x)) % 360


rows = []
for f in sorted((ROOT / "palettes").glob("*.json")):
    p = json.loads(f.read_text())
    # Two generator families wrote two schemas: the older one uses
    # background/foreground/colors, the newer dark-city/fifth-element one
    # uses bg/fg/c. Accept either.
    c = p.get("colors") or p["c"]
    bg = p.get("background") or p["bg"]
    # accent slots: red, green, yellow, blue, magenta, cyan
    accents = [c[1], c[2], c[3], c[4], c[5], c[6]]
    hs = [hsv(a) for a in accents]
    hues = [h for h, s, v in hs]
    sats = [s for h, s, v in hs]
    vals = [v for h, s, v in hs]
    rows.append({
        "name": f.stem,
        "mode": p["mode"],
        "bg_lum": lum(bg),
        "sat": sum(sats) / len(sats),
        "val": sum(vals) / len(vals),
        "hue": warmth(hues, sats),
    })

dark = [r for r in rows if r["mode"] == "dark"]
light = [r for r in rows if r["mode"] == "light"]

for label, group in (("DARK MODES", dark), ("LIGHT MODES", light)):
    print(f"\n=== {label} ===")
    print(f"{'variant':22s} {'bg lum':>7s} {'accent sat':>11s} "
          f"{'accent val':>11s} {'hue':>7s}  character")
    for r in sorted(group, key=lambda r: r["bg_lum"]):
        h = r["hue"]
        temp = ("warm" if h < 60 or h > 330 else
                "cool" if 160 < h < 280 else "mixed")
        print(f"  {r['name']:20s} {r['bg_lum']:.4f} {r['sat']:11.2f} "
              f"{r['val']:11.2f} {h:6.0f}°  {temp}")

print("\n=== gaps ===")
print(f"darkest bg  : {min(rows, key=lambda r: r['bg_lum'])['name']} "
      f"({min(r['bg_lum'] for r in rows):.4f})")
print(f"lightest bg : {max(rows, key=lambda r: r['bg_lum'])['name']} "
      f"({max(r['bg_lum'] for r in rows):.4f})")
print(f"mean dark-mode bg luminance : {sum(r['bg_lum'] for r in dark)/len(dark):.4f}")
print(f"mean light-mode bg luminance: {sum(r['bg_lum'] for r in light)/len(light):.4f}")
print(f"mean accent saturation      : {sum(r['sat'] for r in rows)/len(rows):.2f}")
warm_n = sum(1 for r in rows if r['hue'] < 60 or r['hue'] > 330)
print(f"warm-leaning palettes       : {warm_n}/{len(rows)}")
print("\nNOTE: every 'light' mode here is a desaturated inversion of a dark")
print("film. None was designed light-first, which is why they read as")
print("washed-out rather than genuinely bright.")
