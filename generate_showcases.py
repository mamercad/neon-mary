#!/usr/bin/env python3
"""Generate the showcase desktop SVGs for every variant, in dark AND light.

The README presents one showcase desktop per variant per mode, so both modes
need a real composition -- previously only dark existed, and two of the dark
SVGs still carried an unsubstituted `VAR_PANEL` placeholder from the
hand-filled cinematic template.

Everything is derived from the variant's own palette JSON, so a new variant
picks up a showcase automatically and no placeholder can survive: any VAR_*
token left in the output is a hard error.
"""
import json
import re
import sys
from pathlib import Path

from palette_utils import ratio

ROOT = Path(__file__).resolve().parent
SHOTS = ROOT / "screenshots"

# variant tag -> (display title, wallpaper dir, tagline, wallpaper caption)
VARIANTS = {
    "blade-runner": ("Blade Runner", "", "ALL THOSE MOMENTS, LOST IN TIME.",
                     "neon rain / off-world"),
    "crow": ("The Crow (1994)", "crow", "IT CAN'T RAIN ALL THE TIME.",
             "nightfall / rain"),
    "amelie": ("Amélie (2001)", "amelie", "TIMES ARE HARD FOR DREAMERS.",
               "café / golden hour"),
    "tron": ("Tron (1982)", "tron", "THE GRID IS OPEN.",
             "the grid / end of line"),
    "dark-city": ("Dark City (1998)", "dark-city", "THE CITY IS DREAMING.",
                  "perpetual night / tuning"),
    "fifth-element": ("The Fifth Element (1997)", "fifth-element",
                      "MULTIPASS ACCEPTED.", "electric cyan / solar amber"),
    "grand-budapest": ("The Grand Budapest Hotel (2014)", "grand-budapest",
                       "KEEP YOUR HANDS OFF MY LOBBY BOY.",
                       "confectionery pink / alpine"),
    "evangelion": ("Neon Genesis Evangelion (1995)", "evangelion",
                   "GOD'S IN HIS HEAVEN. ALL'S RIGHT WITH THE WORLD.",
                   "unit-01 purple / nerv black"),
    "matrix": ("The Matrix (1999)", "matrix", "THERE IS NO SPOON.",
               "phosphor green / constructed world"),
    "solaris": ("Solaris (1972)", "solaris", "THE OCEAN REMEMBERS.",
                "amber instrument light / distant ocean"),
    "suspiria": ("Suspiria (1977)", "suspiria", "THE DANCE BEGINS.",
                 "blood red / theatrical shadow"),
}

# palette file stem per variant (base Blade Runner has no prefix)
STEM = {"blade-runner": "", "crow": "crow-", "amelie": "amelie-",
        "tron": "tron-", "dark-city": "dark-city-",
        "fifth-element": "fifth-element-",
        "grand-budapest": "grand-budapest-",
        "evangelion": "evangelion-", "matrix": "matrix-", "solaris": "solaris-",
        "suspiria": "suspiria-"}


def load_palette(tag, mode):
    stem = STEM[tag] + mode
    p = json.loads((ROOT / "palettes" / f"{stem}.json").read_text())
    # Two schemas in the wild: colors/background/foreground vs c/bg/fg.
    c = p.get("colors") or p["c"]
    return {
        "bg": p.get("background") or p["bg"],
        "fg": p.get("foreground") or p["fg"],
        "accent": p["accent"],
        "red": p["red"],
        "c": c,
    }


def mix(a, b, t):
    """Blend two #rrggbb colours."""
    A = [int(a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    B = [int(b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02x%02x%02x" % tuple(
        int(round(A[i] + (B[i] - A[i]) * t)) for i in range(3))


def readable(col, bg, fg, target=4.5):
    """Nudge `col` toward `fg` until it is readable on `bg`."""
    if ratio(col, bg) >= target:
        return col
    out = col
    for step in range(1, 101):
        out = mix(col, fg, step / 100.0)
        if ratio(out, bg) >= target:
            break
    return out


def build(tag, mode):
    title, wdir, tagline, wcap = VARIANTS[tag]
    p = load_palette(tag, mode)
    c = p["c"]
    bg, fg, accent, red = p["bg"], p["fg"], p["accent"], p["red"]
    light = mode == "light"

    # Panels sit slightly off the base surface so windows read as windows.
    panel = mix(bg, "#000000", 0.35) if not light else mix(bg, "#ffffff", 0.55)
    titlebar = mix(bg, "#000000", 0.55) if not light else mix(bg, "#ffffff", 0.30)
    shade_a, shade_b = (bg, mix(bg, "#000000", 0.5)) if not light else (bg, mix(bg, "#ffffff", 0.4))
    shade_o1, shade_o2 = (".72", ".94") if not light else (".55", ".80")
    panel_op = ".94" if not light else ".96"

    # Semantic roles, each forced readable against the panel it sits on.
    green = readable(c[2], panel, fg, 4.5)
    amber = readable(c[3], panel, fg, 4.5)
    violet = readable(c[5], panel, fg, 4.5)
    cyan = readable(c[6], panel, fg, 4.5)
    acc = readable(accent, panel, fg, 5.0)
    err = readable(red, panel, fg, 4.5)
    body = readable(fg, panel, fg, 7.0)
    muted = readable(c[8], panel, fg, 7.0)
    # The top bar and footer sit directly on the wallpaper, not on a panel, so
    # they must be measured against the *shaded wallpaper*, not the panel fill.
    # In light mode the shade lands mid-grey, which is why palette colour 8
    # (tuned for a dark canvas) washes out to ~2.5:1 there.
    barbase = mix(bg, "#000000", 0.25) if not light else mix(bg, "#ffffff", 0.20)
    bar_op = ".42" if not light else ".80"
    bartext = readable(fg, barbase, fg, 7.0)
    barmuted = readable(c[8], barbase, fg, 9.0)

    wall = f"../wallpapers/{wdir}/{mode}/4k.png" if wdir else f"../wallpapers/{mode}/4k.png"
    label = f"{tag}-{mode}" if tag != "blade-runner" else mode
    skin = f"neon-mary-{tag}-{mode}" if tag != "blade-runner" else f"neon-mary-{mode}"

    def t(x, y, fill, size, s, weight=""):
        w = f' font-weight="{weight}"' if weight else ""
        s = (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="monospace" '
                f'font-size="{size}"{w}>{s}</text>')

    cursor = "$ \u2588"
    dot = "\u25cf READY TO DEPLOY"
    rows = [
        (190, [(104, green, "mark@boomer"), (228, violet, " ~/Code/GH/mamercad/neon-mary")]),
        (222, [(104, acc, "$ omarchy theme status")]),
        (258, [(104, body, f"theme      {skin}")]),
        (290, [(104, body, "bar        transparent / top")]),
        (322, [(104, body, f"wallpaper  3840x2160 / {wcap}")]),
        (354, [(104, green, "shell      ok")]),
        (406, [(104, acc, "$ omarchy theme list --mode " + mode)]),
        (442, [(104, body, f"neon-mary-{tag}-dark" if tag != "blade-runner" else "neon-mary-dark")]),
        (474, [(104, body, f"neon-mary-{tag}-light" if tag != "blade-runner" else "neon-mary-light")]),
        (506, [(104, muted, f"mode       {mode}  ({'high key' if light else 'low key'})")]),
        (558, [(104, acc, "$ find terminals omarchy hermes -type f")]),
        (594, [(104, muted, f"terminals/{label}/{{ghostty,kitty,wezterm}}.conf")]),
        (626, [(104, muted, f"omarchy/themes/{skin}")]),
        (658, [(104, muted, f"hermes/skins/{skin}.yaml")]),
        (742, [(104, violet, f"NEON MARY // {tagline}")]),
        (820, [(104, acc, cursor)]),
    ]
    term = "".join(t(x, y, f, 18, s) for y, cells in rows for x, f, s in cells)

    swatches = "".join(
        f'<rect x="{1220 + i * 82}" y="294" width="70" height="70" fill="{v}" '
        f'stroke="{mix(panel, fg, 0.3)}" stroke-width="1"/>'
        for i, v in enumerate([bg, accent, c[5], c[2], c[3], red]))
    legend = "".join(
        t(1220, 404 + i * 32, body, 16, f"{n:<11s} {v}")
        for i, (n, v) in enumerate([
            ("background", bg), ("accent", accent), ("alt", c[5]),
            ("green", c[2]), ("amber", c[3]), ("red", red)]))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">
<defs><linearGradient id="shade" x2="0" y2="1"><stop stop-color="{shade_a}" stop-opacity="{shade_o1}"/><stop offset="1" stop-color="{shade_b}" stop-opacity="{shade_o2}"/></linearGradient><filter id="shadow"><feGaussianBlur in="SourceAlpha" stdDeviation="18"/><feOffset dy="14"/><feComponentTransfer><feFuncA type="linear" slope=".6"/></feComponentTransfer><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<image href="{wall}" width="1920" height="1080" preserveAspectRatio="xMidYMid slice"/><rect width="1920" height="1080" fill="url(#shade)"/>
<rect x="0" y="0" width="1920" height="46" fill="{barbase}" fill-opacity="{bar_op}"/>{t(28, 29, acc, 17, "NEON MARY", "bold")}{t(180, 29, barmuted, 15, "OMARCHY // SYSTEM ONLINE")}{t(1650, 29, bartext, 15, "BOOMER  05:53")}
<g filter="url(#shadow)"><rect x="72" y="104" width="1080" height="780" rx="8" fill="{panel}" fill-opacity="{panel_op}" stroke="{acc}" stroke-width="2"/><rect x="72" y="104" width="1080" height="44" rx="8" fill="{titlebar}"/><circle cx="98" cy="126" r="6" fill="{red}"/><circle cx="120" cy="126" r="6" fill="{c[3]}"/><circle cx="142" cy="126" r="6" fill="{c[2]}"/>{t(178, 132, body, 16, f"ghostty — {skin}")}
{term}</g>
<g filter="url(#shadow)"><rect x="1190" y="184" width="660" height="550" rx="8" fill="{panel}" fill-opacity=".95" stroke="{violet}" stroke-width="2"/><rect x="1190" y="184" width="660" height="44" rx="8" fill="{titlebar}"/>{t(1220, 212, violet, 16, "THEME INSPECTOR")}{t(1220, 274, muted, 15, f"PALETTE / {mode.upper()}")}{swatches}{legend}{t(1220, 608, acc, 16, "TARGETS")}{t(1220, 640, body, 16, "ghostty  kitty  alacritty  wezterm")}{t(1220, 672, body, 16, "omarchy  hermes  vscode  windows-terminal")}{t(1220, 704, green, 16, dot)}</g><rect x="60" y="998" width="720" height="30" rx="5" fill="{barbase}" fill-opacity="{bar_op}"/>{t(74, 1018, bartext, 14, f"EXAMPLE SHOWCASE • NEON MARY / {title.upper()} {mode.upper()}")}</svg>
'''


def main():
    tags = sys.argv[1:] or list(VARIANTS)
    for tag in tags:
        for mode in ("dark", "light"):
            svg = build(tag, mode)
            leftover = re.findall(r"VAR_[A-Z_]+", svg)
            if leftover:
                raise SystemExit(f"!! unsubstituted placeholders in {tag}-{mode}: {set(leftover)}")
            out = SHOTS / f"desktop-{tag}-{mode}-example.svg"
            out.write_text(svg, encoding="utf-8")
            print(f"  wrote {out.name}")


if __name__ == "__main__":
    main()
