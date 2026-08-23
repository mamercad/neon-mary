"""Contrast-audit every Neon Mary Hermes skin against WCAG tiers.

The repo's validate_*.py scripts confirm files exist and wallpapers are the
right dimensions, but never check that the palettes are legible. This does.

Tiers (same as used for the blade-runner skin):
  4.5:1  body text
  3.0:1  accents / headings / semantic state / syntax
  1.9:1  decorative borders (not covered by WCAG non-text contrast)
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
SKINS = sorted((ROOT / "hermes" / "skins").glob("*.yaml"))

BODY = {"ui_text", "banner_text", "ui_label", "status_bar_text"}
BORDER = {"banner_border", "ui_border", "session_border", "response_border"}
SURFACE = {"background", "status_bar_bg", "completion_menu_bg",
           "completion_menu_current_bg", "completion_menu_meta_bg",
           "diff_added", "diff_removed"}


def srgb_lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def lum(hx):
    hx = hx.lstrip("#")
    r, g, b = (int(hx[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * srgb_lin(r) + 0.7152 * srgb_lin(g) + 0.0722 * srgb_lin(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


total_fail = 0
for path in SKINS:
    # A skin that will not parse is a hard failure: Hermes silently falls back
    # to `default`, so a broken palette looks like "the theme didn't apply".
    # This is exactly how six invalid skins shipped -- an unquoted YAML
    # `description:` containing a colon.
    try:
        d = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        first = str(exc).split("\n")[0]
        print(f"\n{path.name:34s} INVALID YAML -- {first}")
        total_fail += 1
        continue
    colors = d.get("colors", {})
    bg = colors.get("background")
    if not bg:
        print(f"{path.name}: NO BACKGROUND")
        total_fail += 1
        continue
    fails = []
    for k, v in colors.items():
        if k in SURFACE or not isinstance(v, str) or not v.startswith("#"):
            continue
        r = ratio(v, bg)
        need = 4.5 if k in BODY else 1.9 if k in BORDER else 3.0
        if r < need:
            fails.append((k, v, r, need))
    status = "PASS" if not fails else f"{len(fails)} FAIL"
    print(f"\n{path.name:34s} bg={bg}  {status}")
    for k, v, r, need in fails:
        tier = "body" if k in BODY else "border" if k in BORDER else "accent"
        print(f"    {k:26s} {v}  {r:5.2f}:1  < {need} ({tier})")
    total_fail += len(fails)

print(f"\n{'=' * 60}")
print(f"total failures across {len(SKINS)} skins: {total_fail}")
sys.exit(1 if total_fail else 0)
