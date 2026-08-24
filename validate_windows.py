"""Verify the generated Windows artifacts decode back to the source palette."""
import configparser
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WIN = ROOT / "windows"

STEM = {"blade-runner": "", "crow": "crow-", "amelie": "amelie-",
        "tron": "tron-", "dark-city": "dark-city-",
        "fifth-element": "fifth-element-", "grand-budapest": "grand-budapest-"}

fails = []
checked = 0

for tag, stem in STEM.items():
    for mode in ("dark", "light"):
        pal = json.loads((ROOT / "palettes" / f"{stem}{mode}.json").read_text())
        bg = pal.get("background") or pal["bg"]
        accent = pal["accent"]
        ar, ag, ab = (int(accent.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))

        # --- .theme parses as INI and carries the right mode + bg ---
        tf = WIN / f"{tag}-{mode}.theme"
        cp = configparser.ConfigParser(strict=False, interpolation=None)
        cp.optionxform = str  # type: ignore[assignment]  # preserve key case
        try:
            cp.read_string(tf.read_text(encoding="utf-8"))
        except Exception as e:
            fails.append(f"{tf.name}: INI parse error: {e}")
            continue
        for req in ("Theme", "Control Panel\\Desktop", "VisualStyles",
                    "Control Panel\\Colors", "MasterThemeSelector"):
            if req not in cp:
                fails.append(f"{tf.name}: missing required section [{req}]")
        want = "Light" if mode == "light" else "Dark"
        got = cp["VisualStyles"].get("SystemMode")
        if got != want:
            fails.append(f"{tf.name}: SystemMode={got}, expected {want}")
        want_bg = "%d %d %d" % tuple(int(bg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        got_bg = cp["Control Panel\\Colors"].get("Background")
        if got_bg != want_bg:
            fails.append(f"{tf.name}: Background={got_bg}, expected {want_bg}")

        # --- .reg AccentPalette decodes back to the accent at index 5 ---
        rf = WIN / f"{tag}-{mode}.reg"
        txt = rf.read_text(encoding="utf-8")
        m = re.search(r'"AccentPalette"=hex:([0-9a-f,\\\s]+)', txt)
        if not m:
            fails.append(f"{rf.name}: no AccentPalette")
            continue
        blob = re.sub(r"[\\\s]", "", m.group(1))
        by = [int(x, 16) for x in blob.split(",") if x]
        if len(by) != 32:
            fails.append(f"{rf.name}: AccentPalette is {len(by)} bytes, expected 32")
        else:
            # index 5 of 8 quads == bytes 16..19, stored BGR0
            b, g, r, z = by[16:20]
            if (r, g, b) != (ar, ag, ab):
                fails.append(f"{rf.name}: palette[4] decodes #{r:02x}{g:02x}{b:02x}, "
                             f"expected {accent}")
            if z != 0:
                fails.append(f"{rf.name}: palette[4] 4th byte {z}, expected 0")

        # --- AccentColorMenu is 0xAABBGGRR of the same accent ---
        m2 = re.search(r'"AccentColorMenu"=dword:([0-9a-f]{8})', txt)
        if not m2:
            fails.append(f"{rf.name}: no AccentColorMenu")
        else:
            v = int(m2.group(1), 16)
            rr, gg, bb = v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF
            if (rr, gg, bb) != (ar, ag, ab):
                fails.append(f"{rf.name}: AccentColorMenu decodes "
                             f"#{rr:02x}{gg:02x}{bb:02x}, expected {accent}")

        # --- mode flags ---
        want_flag = f"dword:{1 if mode == 'light' else 0:08x}"
        for key in ("AppsUseLightTheme", "SystemUsesLightTheme"):
            if f'"{key}"={want_flag}' not in txt:
                fails.append(f"{rf.name}: {key} not {want_flag}")

        # --- CRLF, as Windows INI/reg expect ---
        for f in (tf, rf):
            raw = f.read_bytes()
            if b"\r\n" not in raw:
                fails.append(f"{f.name}: not CRLF line endings")
        checked += 1

print(f"checked {checked} variant/mode pairs ({checked * 2} files)")
if fails:
    print(f"\n{len(fails)} FAILURES:")
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("all Windows artifacts decode back to their source palette")
