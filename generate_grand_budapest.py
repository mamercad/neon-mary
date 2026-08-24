#!/usr/bin/env python3
"""Generate the Neon Mary: The Grand Budapest Hotel (2014) variant.

Unlike the other variants this one is designed LIGHT-FIRST. Every existing
palette in the repo is a dark film, and its "light" mode is an inversion --
which is why they read washed out. Grand Budapest is genuinely a bright film,
so the light mode is the primary design and the dark mode is the counterpart.

PALETTE SOURCE
--------------
Measured from 33 publicity/production stills via TMDB (the theatrical poster
was identified by inspection and excluded). There is no archival print of this
title in the ERC FilmColors corpus, so unlike the Blade Runner study these are
colour-managed digital sources rather than a dye-faded print: no fade
correction is needed, but the result reflects design intent rather than a
frame-accurate colorimetric record of a graded release print.

Measured, saturation-weighted:

    mean luminance            0.518   (vs ~0.004 for every other variant bg)
    pixels above v>0.60       43.7%
    high key   v>0.80         20.0%
    crushed shadow v<0.15     13.8%
    warm chromatic            71.4%
    cool chromatic            14.6%

    coral / salmon    hue  25.0   #976038   23.0% of accents
    red / crimson     hue  15.4   #a45f47   16.5%
    lacquer red       hue   2.5   #aa1711   14.9%
    rose              hue 356.2   #cf555d   12.9%
    alpine blue       hue 204.9   #467ca3   10.0%
    amber / gold      hue  33.8   #845f2f    7.8%
    teal              hue 198.0   #4394b7    3.9%

The film's signature façade pink (#f1a7be) and the aubergine staff uniform
(#5c2a73) are design landmarks confirmed by inspection of the stills; the
aubergine is deliberately kept as the violet slot because it is the film's
most recognisable single colour.

Anderson shot each era in a different aspect ratio, so the two modes lean on
different periods rather than being a plain inversion: light = the 1932
confectionery pink, dark = the 1968 burnt-orange lobby.
"""
import json
import shutil
import subprocess
from pathlib import Path

from palette_utils import light_grade_args, muted

ROOT = Path(__file__).resolve().parent
SOURCE = Path.home() / "Pictures" / "mary.png"
RESOLUTIONS = {"4k": (3840, 2160), "wqhd": (2560, 1440), "qhd": (1920, 1080),
               "16-10": (2560, 1600), "3-2": (2160, 1440), "4-3": (2048, 1536),
               "1-1": (2048, 2048), "9-16": (1440, 2560)}

PALETTES = {
    # LIGHT is the primary design: 1932 Mendl's-box pink, warm and high key.
    "light": {
        "background": "#fdf0f2", "foreground": "#3a2228",
        "accent": "#b0356b", "red": "#aa1711",
        "colors": [
            "#fdf0f2",  # 0 base
            "#aa1711",  # 1 lacquer red (key racks / elevator)
            "#4a7343",  # 2 alpine green
            "#9a6a12",  # 3 Mendl's gold
            "#2f6f96",  # 4 alpine blue
            "#5c2a73",  # 5 aubergine uniform
            "#2b7f86",  # 6 teal
            "#3a2228",  # 7 ink
            "#8a6b76",  # 8 muted mauve (readable on near-white)
            "#c4342c",  # 9 bright lacquer
            "#5f8f55",  # 10
            "#b8861f",  # 11
            "#3f86b0",  # 12
            "#7b3f96",  # 13
            "#38a0a8",  # 14
            "#2a171c",  # 15
        ],
    },
    # DARK is the 1968 era: burnt orange and oxblood, still warm.
    "dark": {
        "background": "#22161a", "foreground": "#f7e4e6",
        "accent": "#f1a7be", "red": "#e04a3f",
        "colors": [
            "#22161a",
            "#e04a3f",
            "#8fbf7a",
            "#e0b455",
            "#6fa8cd",
            "#b47fd0",
            "#63c3c9",
            "#f7e4e6",
            "#5a3f47",
            "#f2705f",
            "#a8d693",
            "#f5cd7a",
            "#93c4e2",
            "#cb9ee0",
            "#88dade",
            "#fff5f6",
        ],
    },
}

TITLE = "The Grand Budapest Hotel (2014)"
TAG = "grand-budapest"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rgb(v):
    return tuple(int(v[i:i + 2], 16) / 255 for i in (1, 3, 5))


def toml(p):
    lines = [f'mode = "{p["mode"]}"', "",
             f'background = "{p["background"]}"',
             f'foreground = "{p["foreground"]}"', "",
             f'accent = "{p["accent"]}"', f'red     = "{p["red"]}"', ""]
    lines += [f'color{i:<2} = "{v}"' for i, v in enumerate(p["colors"])]
    return "\n".join(lines) + "\n"


def ghostty(p):
    return "\n".join([f"background = {p['background']}",
                      f"foreground = {p['foreground']}",
                      f"cursor-color = {p['accent']}",
                      f"selection-background = {p['accent']}",
                      *[f"palette = {i}={v}" for i, v in enumerate(p['colors'])]]) + "\n"


def kitty(p):
    return "\n".join([f"foreground {p['foreground']}",
                      f"background {p['background']}",
                      f"cursor {p['accent']}",
                      f"selection_foreground {p['background']}",
                      f"selection_background {p['accent']}",
                      *[f"color{i} {v}" for i, v in enumerate(p['colors'])]]) + "\n"


def alacritty(p):
    c = p["colors"]
    n = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    return ("[colors.primary]\nbackground = '" + p["background"] +
            "'\nforeground = '" + p["foreground"] +
            "'\n\n[colors.cursor]\ntext = '" + p["background"] +
            "'\ncursor = '" + p["accent"] + "'\n\n[colors.normal]\n" +
            "\n".join(f"{a} = '{b}'" for a, b in zip(n, c[:8])) +
            "\n\n[colors.bright]\n" +
            "\n".join(f"{a} = '{b}'" for a, b in zip(n, c[8:])) + "\n")


def wezterm(p):
    c = p["colors"]
    return ("return {\n  foreground = '" + p["foreground"] +
            "',\n  background = '" + p["background"] +
            "',\n  cursor_bg = '" + p["accent"] +
            "',\n  cursor_fg = '" + p["background"] +
            "',\n  ansi = {" + ", ".join(repr(v) for v in c[:8]) +
            "},\n  brights = {" + ", ".join(repr(v) for v in c[8:]) + "},\n}\n")


def windows(p):
    c = p["colors"]
    n = ["black", "red", "green", "yellow", "blue", "purple", "cyan", "white"]
    d = {"name": f"Neon Mary: {TITLE}", "background": p["background"],
         "foreground": p["foreground"], "cursorColor": p["accent"]}
    d.update(dict(zip(n, c[:8])))
    d.update(dict(zip(["bright" + x.title() for x in n], c[8:])))
    return json.dumps(d, indent=2) + "\n"


def hermes(p, mode):
    c = p["colors"]
    dim = muted(c[8], p["background"], p["foreground"])
    # Slot 14 is the "bright" ANSI cyan, which is designed to sit on a dark
    # canvas. On this light-first palette it lands at 2.8:1 against the near
    # white background, so headings use the deep aubergine instead -- which is
    # also the film's most recognisable colour.
    heading = c[5] if mode == "light" else c[14]
    return f'''name: neon-mary-{TAG}-{mode}
description: "Neon Mary: {TITLE} — confectionery pink, aubergine, and lacquer red ({mode})."
colors:
  background: '{p["background"]}'
  status_bar_bg: '{p["background"]}'
  ui_accent: '{p["accent"]}'
  banner_accent: '{p["accent"]}'
  prompt: '{p["accent"]}'
  input_rule: '{p["red"]}'
  banner_title: '{heading}'
  ui_primary: '{heading}'
  session_label: '{heading}'
  response_border: '{c[6]}'
  banner_text: '{p["foreground"]}'
  ui_text: '{p["foreground"]}'
  ui_label: '{c[7]}'
  banner_dim: '{dim}'
  banner_border: '{c[6]}'
  ui_border: '{c[6]}'
  session_border: '{c[6]}'
  ui_tool: '{c[5]}'
  ui_thinking: '{c[13]}'
  ui_ok: '{c[2]}'
  ui_warn: '{c[3]}'
  ui_error: '{p["red"]}'
  status_bar_text: '{c[7]}'
  status_bar_good: '{c[2]}'
  status_bar_warn: '{c[3]}'
  status_bar_bad: '{c[9]}'
  status_bar_critical: '{p["red"]}'
  syntax_string: '{c[2]}'
  syntax_number: '{c[3]}'
  syntax_keyword: '{c[5]}'
  syntax_comment: '{dim}'
  completion_menu_bg: '{p["background"]}'
  completion_menu_current_bg: '{c[6]}'
  completion_menu_meta_bg: '{p["background"]}'
branding:
  agent_name: Hermes Agent
  prompt_symbol: ❯
  welcome: Keep your hands off my lobby boy.
  goodbye: You see, there are still faint glimmers of civilization left.
  help_header: "◤ Neon Mary: Grand Budapest — Commands"
spinner:
  waiting_faces: ["(◉)", "(◎)", "(⊙)"]
  thinking_faces: ["(⌁)", "(⊹)"]
  thinking_verbs: [concierging, arranging, absconding, perfuming]
  wings: [["⟪◤", "◥⟫"], ["⟪△", "△⟫"]]
tool_prefix: ┊
'''


def wallpaper(source, out, w, h, mode, light_bg):
    out.parent.mkdir(parents=True, exist_ok=True)
    is4k = (w, h) == (3840, 2160)
    base = source if is4k else ROOT / "wallpapers" / TAG / mode / "4k.png"
    # Grade only on the 4k pass; smaller sizes derive from the graded 4k.
    if not is4k:
        grade = []
    elif mode == "dark":
        grade = ["-modulate", "104,88,100"]
    else:
        grade = light_grade_args(light_bg)
    subprocess.run(["magick", str(base), "-resize", f"{w}x{h}^", "-gravity",
                    "center", "-extent", f"{w}x{h}", *grade, str(out)],
                   check=True)


def main():
    if not SOURCE.exists():
        raise SystemExit(f"Missing source: {SOURCE}")
    light_bg = PALETTES["light"]["background"]
    for mode, base in PALETTES.items():
        p = dict(base)
        p["mode"] = mode
        write(ROOT / "palettes" / f"{TAG}-{mode}.json", json.dumps(p, indent=2) + "\n")
        write(ROOT / "hermes" / "skins" / f"neon-mary-{TAG}-{mode}.yaml", hermes(p, mode))
        om = ROOT / "omarchy" / "themes" / f"neon-mary-{TAG}-{mode}"
        (om / "backgrounds").mkdir(parents=True, exist_ok=True)
        write(om / "colors.toml", toml(p))
        write(om / "icons.theme", "Yaru-magenta\n")
        files = {
            "ghostty.conf": ghostty(p), "kitty.conf": kitty(p),
            "alacritty.toml": alacritty(p), "wezterm.lua": wezterm(p),
            "windows-terminal.json": windows(p),
            "fzf.conf": (f"--color=bg:{p['background']},fg:{p['foreground']},"
                         f"hl:{p['accent']},border:{p['accent']},"
                         f"prompt:{p['accent']},pointer:{p['red']}\n"),
            "iterm2.json": json.dumps({
                "Name": f"Neon Mary: {TITLE} {mode}",
                "Background Color": dict(zip(("Red Component", "Green Component", "Blue Component"), rgb(p["background"]))),
                "Foreground Color": dict(zip(("Red Component", "Green Component", "Blue Component"), rgb(p["foreground"]))),
            }, indent=2) + "\n",
            "Terminal.app.terminal": json.dumps({
                "name": f"Neon Mary: {TITLE} {mode}",
                "profile": f"Neon Mary: {TITLE}", "colors": p["colors"],
            }, indent=2) + "\n",
        }
        for name, content in files.items():
            write(ROOT / "terminals" / TAG / mode / name, content)
        write(ROOT / "editors" / TAG / mode / "vscode-color-theme.json",
              json.dumps({"name": f"Neon Mary: {TITLE} {mode}", "type": mode,
                          "colors": {"editor.background": p["background"],
                                     "editor.foreground": p["foreground"],
                                     "terminal.ansiCyan": p["colors"][6],
                                     "terminal.ansiMagenta": p["colors"][5],
                                     "terminal.ansiRed": p["red"],
                                     "terminal.ansiGreen": p["colors"][2]},
                          "tokenColors": []}, indent=2) + "\n")
        write(ROOT / "editors" / TAG / mode / "vim.vim",
              f'" Neon Mary: {TITLE} {mode} palette\n'
              f'let g:neon_mary_grand_budapest_background = "{p["background"]}"\n'
              f'let g:neon_mary_grand_budapest_foreground = "{p["foreground"]}"\n')
        write(ROOT / "editors" / TAG / mode / "tmux.conf",
              f'set -g status-style "bg={p["background"]},fg={p["foreground"]}"\n'
              f'set -g pane-active-border-style "fg={p["accent"]}"\n'
              f'set -g message-style "bg={p["background"]},fg={p["accent"]}"\n')
        for name, (w, h) in RESOLUTIONS.items():
            out = ROOT / "wallpapers" / TAG / mode / f"{name}.png"
            wallpaper(SOURCE, out, w, h, mode, light_bg)
            shutil.copy2(out, om / "backgrounds" / f"{name}.png")
    write(ROOT / "omarchy" / f"{TAG}-README.md",
          f"# Neon Mary: {TITLE}\n\nNeon Mary is the theme family; these are the "
          f"{TITLE} variant native Omarchy packages. This variant is designed "
          f"light-first — the light mode is the primary treatment.\n")


if __name__ == "__main__":
    main()
