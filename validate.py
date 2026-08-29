#!/usr/bin/env python3
"""Structural check across every Neon Mary variant.

Replaces the per-variant validate_*.py scripts. Those were copy-pasted, so
each new variant either got a near-identical file or was silently left
unchecked -- validate_evangelion.py existed while nothing verified that
Evangelion was wired into the shared tooling at all.

This checks, for every variant in both modes:
  * the palette JSON exists, parses, and its `mode` field is self-consistent
  * all 8 wallpaper resolutions exist at exactly the right pixel size, in
    both wallpapers/ and the Omarchy package's backgrounds/
  * the Hermes skin exists
  * the Omarchy package carries colors.toml
  * terminal and editor exports exist
  * the variant is registered in the shared tooling, so a new variant cannot
    quietly skip showcases, Windows artifacts, or the README
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent

RESOLUTIONS = {"4k": (3840, 2160), "wqhd": (2560, 1440), "qhd": (1920, 1080),
               "16-10": (2560, 1600), "3-2": (2160, 1440), "4-3": (2048, 1536),
               "1-1": (2048, 2048), "9-16": (1440, 2560)}

# tag -> (wallpaper subdir, palette stem, terminal/editor subdir)
# Blade Runner is the original layout: no subdir, unprefixed palette stem.
VARIANTS = {
    "blade-runner":   ("",              "",              ""),
    "crow":           ("crow",          "crow-",          "crow"),
    "amelie":         ("amelie",        "amelie-",        "amelie"),
    "tron":           ("tron",          "tron-",          "tron"),
    "dark-city":      ("dark-city",     "dark-city-",     "dark-city"),
    "fifth-element":  ("fifth-element", "fifth-element-", "fifth-element"),
    "grand-budapest": ("grand-budapest","grand-budapest-","grand-budapest"),
    "evangelion":     ("evangelion",    "evangelion-",    "evangelion"),
    "matrix":         ("matrix",        "matrix-",        "matrix"),
    "solaris":        ("solaris",       "solaris-",    "solaris"),
    "suspiria":       ("suspiria",      "suspiria-",   "suspiria"),
}

# Files that must mention every variant, so nothing ships half-wired.
REGISTRIES = ["generate_showcases.py", "generate_windows.py",
              "measure_wallpapers.py", "README.md"]

# The PowerShell installers gate -Variant on a hardcoded ValidateSet, so a
# variant missing there is rejected at the command line even though every
# artifact exists on disk. That is exactly how Evangelion shipped complete
# but uninstallable on Windows, so the list is asserted rather than assumed.
PS_VALIDATESETS = ["windows/apply-theme.ps1", "windows/apply-terminal.ps1"]

TERMINAL_FILES = ["ghostty.conf", "kitty.conf", "alacritty.toml",
                  "wezterm.lua", "windows-terminal.json"]

fails: list[str] = []


def check(cond, msg):
    if not cond:
        fails.append(msg)
    return cond


for tag, (wdir, stem, tdir) in VARIANTS.items():
    for mode in ("dark", "light"):
        # --- palette ---
        pal_path = ROOT / "palettes" / f"{stem}{mode}.json"
        if not check(pal_path.exists(), f"{tag}/{mode}: missing {pal_path.name}"):
            continue
        try:
            pal = json.loads(pal_path.read_text())
        except Exception as e:
            fails.append(f"{tag}/{mode}: {pal_path.name} does not parse: {e}")
            continue
        check(pal.get("mode") == mode,
              f"{tag}/{mode}: palette mode field is {pal.get('mode')!r}")
        check((pal.get("background") or pal.get("bg")),
              f"{tag}/{mode}: palette has no background")

        # The showcase legend renders `accent` and ANSI 5 as two labelled
        # swatches, so identical values advertise two colours and draw one.
        cols = pal.get("colors") or pal.get("c") or []
        if pal.get("accent") and len(cols) > 5:
            check(pal["accent"].lower() != cols[5].lower(),
                  f"{tag}/{mode}: accent and ANSI 5 are both "
                  f"{pal['accent']} -- legend swatches would be identical")

        # --- wallpapers, both locations, exact sizes ---
        wall_base = (ROOT / "wallpapers" / wdir / mode) if wdir else \
                    (ROOT / "wallpapers" / mode)
        om = ROOT / "omarchy" / "themes" / (
            f"neon-mary-{tag}-{mode}" if tag != "blade-runner"
            else f"neon-mary-{mode}")
        for name, size in RESOLUTIONS.items():
            for base in (wall_base, om / "backgrounds"):
                path = base / f"{name}.png"
                if not check(path.exists(),
                             f"{tag}/{mode}: missing {path.relative_to(ROOT)}"):
                    continue
                with Image.open(path) as im:
                    check(im.size == size,
                          f"{tag}/{mode}: {path.relative_to(ROOT)} is "
                          f"{im.size}, expected {size}")

        # --- Omarchy package + Hermes skin ---
        check((om / "colors.toml").exists(),
              f"{tag}/{mode}: missing {om.name}/colors.toml")
        skin = ROOT / "hermes" / "skins" / (
            f"neon-mary-{tag}-{mode}.yaml" if tag != "blade-runner"
            else f"neon-mary-{mode}.yaml")
        check(skin.exists(), f"{tag}/{mode}: missing {skin.name}")

        # --- terminal + editor exports ---
        tbase = (ROOT / "terminals" / tdir / mode) if tdir else \
                (ROOT / "terminals" / mode)
        for f in TERMINAL_FILES:
            check((tbase / f).exists(),
                  f"{tag}/{mode}: missing {(tbase / f).relative_to(ROOT)}")

        # Windows Terminal keys schemes by name, so dark and light must differ.
        wt = tbase / "windows-terminal.json"
        if wt.exists():
            try:
                nm = json.loads(wt.read_text()).get("name", "")
                check(nm.endswith(mode),
                      f"{tag}/{mode}: WT scheme name {nm!r} is not "
                      f"mode-suffixed; dark and light would collide")
            except Exception as e:
                fails.append(f"{tag}/{mode}: {wt.name} does not parse: {e}")

    # --- registered in the shared tooling? ---
    for reg in REGISTRIES:
        txt = (ROOT / reg).read_text()
        needle = tag if tag != "blade-runner" else "blade-runner"
        check(needle in txt,
              f"{tag}: not referenced in {reg} -- it would be skipped")

    # --- accepted by the PowerShell installers' -Variant ValidateSet? ---
    for ps in PS_VALIDATESETS:
        txt = (ROOT / ps).read_text()
        m = re.search(r"ValidateSet\(([^)]*)\)", txt, re.S)
        if not m:
            fails.append(f"{ps}: no ValidateSet found")
            continue
        allowed = re.findall(r"'([^']+)'", m.group(1))
        check(tag in allowed,
              f"{tag}: missing from {ps} -Variant ValidateSet -- the "
              f"installer would reject it despite the artifacts existing")

print(f"checked {len(VARIANTS)} variants x 2 modes")
if fails:
    print(f"\n{len(fails)} FAILURES:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("validated: palettes, wallpapers, Omarchy packages, Hermes skins, "
      "terminal/editor exports, and shared-tooling registration")
