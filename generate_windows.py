#!/usr/bin/env python3
"""Emit Windows 11 theming artifacts for every Neon Mary variant.

WHAT WINDOWS 11 ACTUALLY LETS YOU THEME
---------------------------------------
Three separate layers, with very different support levels. This script only
touches the first two, which are documented and reversible.

1. `.theme` files -- FULLY SUPPORTED, no patching.
   An INI documented at learn.microsoft.com/windows/win32/controls/
   themesfileformat-overview. Sets the wallpaper, the light/dark mode, the
   accent colour, and the legacy [Control Panel\\Colors] table. Dropped into
   %LOCALAPPDATA%\\Microsoft\\Windows\\Themes and double-clicked, it appears in
   Settings > Personalization > Themes like any built-in theme.

   Caveat worth stating plainly: [Control Panel\\Colors] only governs classic
   / high-contrast surfaces. On a default Windows 11 install most of those
   keys are inert -- the modern shell does not read them. The keys that
   actually move the UI are the wallpaper, the mode, and the accent.

2. Accent + mode registry -- SUPPORTED, no patching.
   The accent is what genuinely tints Windows 11 chrome: taskbar, Start
   highlights, focus rings, title bars, selection. Written to
   HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Accent as
   `AccentPalette`, a 32-byte blob of eight BGR0 quads running dark -> light,
   plus `AccentColorMenu` and `StartColorMenu` DWORDs in 0xAABBGGRR order
   (note: B and R are swapped relative to HTML hex). Mode is
   AppsUseLightTheme / SystemUsesLightTheme under
   ...\\CurrentVersion\\Themes\\Personalize, and ColorPrevalence enables accent
   on the taskbar and title bars.

3. Full visual styles (.msstyles) -- NOT SUPPORTED without patching the OS.
   Restyling actual window frames, the Start flyout, or Explorer's chrome
   needs a third-party signature bypass such as SecureUxTheme or the Windhawk
   UXTheme hook. That patches system theme validation, can break on feature
   updates, and is out of scope here. This script deliberately generates
   nothing that requires it.

So: wallpaper, mode, accent and terminal colours are fully themeable with
supported mechanisms. Window frames and shell chrome are not, without
third-party patching we are not going to ship.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "windows"

VARIANTS = {
    "blade-runner": ("Blade Runner", "", ""),
    "crow": ("The Crow (1994)", "crow", "crow-"),
    "amelie": ("Amélie (2001)", "amelie", "amelie-"),
    "tron": ("Tron (1982)", "tron", "tron-"),
    "dark-city": ("Dark City (1998)", "dark-city", "dark-city-"),
    "fifth-element": ("The Fifth Element (1997)", "fifth-element", "fifth-element-"),
    "grand-budapest": ("The Grand Budapest Hotel (2014)", "grand-budapest",
                       "grand-budapest-"),
    "evangelion": ("Neon Genesis Evangelion (1995)", "evangelion",
                   "evangelion-"),
    "matrix": ("The Matrix (1999)", "matrix", "matrix-"),
    "solaris": ("Solaris (1972)", "solaris", "solaris-"),
    "suspiria": ("Suspiria (1977)", "suspiria", "suspiria-"),
    "akira": ("Akira (1988)", "akira", "akira-"),
    "dune": ("Dune (2021)", "dune", "dune-"),
    "shining": ("The Shining (1980)", "shining", "shining-"),
}


def load(tag, mode):
    _, _, stem = VARIANTS[tag]
    p = json.loads((ROOT / "palettes" / f"{stem}{mode}.json").read_text())
    return {
        "bg": p.get("background") or p["bg"],
        "fg": p.get("foreground") or p["fg"],
        "accent": p["accent"],
        "red": p["red"],
        "c": p.get("colors") or p["c"],
    }


def rgb(hx):
    hx = hx.lstrip("#")
    return tuple(int(hx[i:i + 2], 16) for i in (0, 2, 4))


def triplet(hx):
    """[Control Panel\\Colors] wants 'R G B' decimal."""
    return "%d %d %d" % rgb(hx)


def mix(a, b, t):
    A, B = rgb(a), rgb(b)
    return "#%02x%02x%02x" % tuple(
        int(round(A[i] + (B[i] - A[i]) * t)) for i in range(3))


def accent_palette(accent):
    """32-byte AccentPalette: eight BGR0 quads, darkest -> lightest.

    Windows uses index 5 as the primary accent (the value mirrored into
    AccentColorMenu), with darker shades below and tints above.
    """
    ramp = [mix(accent, "#000000", f) for f in (0.60, 0.45, 0.30, 0.15)]
    ramp += [accent]
    ramp += [mix(accent, "#ffffff", f) for f in (0.25, 0.50, 0.75)]
    out = []
    for hx in ramp:
        r, g, b = rgb(hx)
        out += [b, g, r, 0x00]          # BGR0, little-endian per channel
    return out, ramp


def abgr(hx):
    """Windows DWORD colour order is 0xAABBGGRR -- R and B swapped vs HTML."""
    r, g, b = rgb(hx)
    return f"0x{0xFF:02x}{b:02x}{g:02x}{r:02x}"


def theme_file(tag, mode, p):
    title, _, _ = VARIANTS[tag]
    light = mode == "light"
    name = f"Neon Mary - {title} ({mode})"
    wall = f"%LOCALAPPDATA%\\Microsoft\\Windows\\Themes\\NeonMary\\{tag}-{mode}.jpg"
    c = p["c"]
    # Legacy classic-surface table. Inert on a default Win11 shell, but it is
    # what High Contrast and classic dialogs read, so keep it coherent.
    colors = {
        "Background": p["bg"],
        "Window": p["bg"],
        "WindowText": p["fg"],
        "Hilight": p["accent"],
        "HilightText": p["bg"] if light else p["fg"],
        "ButtonFace": mix(p["bg"], p["fg"], 0.08),
        "ButtonText": p["fg"],
        "GrayText": c[8],
        "ActiveTitle": p["accent"],
        "TitleText": p["bg"] if light else p["fg"],
        "InactiveTitle": mix(p["bg"], p["fg"], 0.18),
        "InactiveTitleText": c[8],
        "MenuText": p["fg"],
        "InfoText": p["fg"],
        "InfoWindow": mix(p["bg"], p["fg"], 0.05),
        "WindowFrame": mix(p["bg"], p["fg"], 0.30),
        "Scrollbar": mix(p["bg"], p["fg"], 0.12),
        "AppWorkspace": mix(p["bg"], p["fg"], 0.10),
    }
    lines = [
        "; Neon Mary theme for Windows 11.",
        "; Generated by generate_windows.py -- do not edit by hand.",
        ";",
        "; Install: place alongside its .jpg in",
        ";   %LOCALAPPDATA%\\Microsoft\\Windows\\Themes\\NeonMary\\",
        "; then double-click this file.",
        ";",
        "; NOTE: [Control Panel\\Colors] below only affects classic and",
        "; high-contrast surfaces. The modern Windows 11 shell ignores most of",
        "; it -- the wallpaper, the light/dark mode and the accent colour are",
        "; what actually change the look. Run apply-accent.ps1 for the accent.",
        "",
        "[Theme]",
        f"DisplayName={name}",
        "",
        "[Control Panel\\Desktop]",
        f"Wallpaper={wall}",
        "TileWallpaper=0",
        "WallpaperStyle=10",
        "",
        "[VisualStyles]",
        "Path=%SystemRoot%\\resources\\themes\\Aero\\Aero.msstyles",
        "ColorStyle=NormalColor",
        "Size=NormalSize",
        f"AutoColorization={0}",
        f"SystemMode={'Light' if light else 'Dark'}",
        f"AppMode={'Light' if light else 'Dark'}",
        "",
        "[Control Panel\\Colors]",
    ]
    lines += [f"{k}={triplet(v)}" for k, v in colors.items()]
    lines += ["", "[MasterThemeSelector]", "MTSM=DABJDKT", ""]
    return "\r\n".join(lines)


def reg_file(tag, mode, p):
    title, _, _ = VARIANTS[tag]
    light = mode == "light"
    pal, ramp = accent_palette(p["accent"])
    blob = ",".join(f"{b:02x}" for b in pal)
    # wrap the hex blob the way .reg files do
    wrapped, line = [], ""
    for chunk in blob.split(","):
        if len(line) + len(chunk) + 1 > 72:
            wrapped.append(line + ",\\")
            line = "  " + chunk
        else:
            line = chunk if not line else line + "," + chunk
    wrapped.append(line)
    hexblob = "\r\n".join(wrapped)
    return "\r\n".join([
        "Windows Registry Editor Version 5.00",
        "",
        f"; Neon Mary - {title} ({mode})",
        "; Generated by generate_windows.py -- do not edit by hand.",
        ";",
        "; Sets the Windows 11 accent colour and light/dark mode. Both are",
        "; supported, per-user (HKCU) and fully reversible -- no OS patching.",
        "; Sign out and back in, or restart Explorer, for the taskbar to pick",
        "; up the new accent.",
        ";",
        f"; accent ramp (dark -> light): {' '.join(ramp)}",
        "",
        "[HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Accent]",
        f'"AccentPalette"=hex:{hexblob}',
        f'"StartColorMenu"=dword:{abgr(ramp[4])[2:]}',
        f'"AccentColorMenu"=dword:{abgr(ramp[4])[2:]}',
        "",
        "[HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize]",
        f'"AppsUseLightTheme"=dword:{1 if light else 0:08x}',
        f'"SystemUsesLightTheme"=dword:{1 if light else 0:08x}',
        '"ColorPrevalence"=dword:00000001',
        "",
        "[HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\DWM]",
        f'"AccentColor"=dword:{abgr(ramp[4])[2:]}',
        f'"ColorizationColor"=dword:{abgr(ramp[4])[2:]}',
        f'"ColorizationAfterglow"=dword:{abgr(ramp[4])[2:]}',
        '"ColorPrevalence"=dword:00000001',
        "",
    ])


def main():
    tags = sys.argv[1:] or list(VARIANTS)
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for tag in tags:
        _, wdir, _ = VARIANTS[tag]
        for mode in ("dark", "light"):
            p = load(tag, mode)
            (OUT / f"{tag}-{mode}.theme").write_text(theme_file(tag, mode, p),
                                                     encoding="utf-8")
            (OUT / f"{tag}-{mode}.reg").write_text(reg_file(tag, mode, p),
                                                   encoding="utf-8")
            n += 2
    print(f"wrote {n} files to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
