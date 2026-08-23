#!/usr/bin/env python3
"""Generate the Neon Mary: The Crow (1994) variant."""
from pathlib import Path
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCE = Path.home() / "Pictures" / "mary.png"
RESOLUTIONS = {"4k": (3840, 2160), "wqhd": (2560, 1440), "qhd": (1920, 1080), "16-10": (2560, 1600), "3-2": (2160, 1440), "4-3": (2048, 1536), "1-1": (2048, 2048), "9-16": (1440, 2560)}
PALETTES = {
    "dark": {
        "background": "#08080d", "foreground": "#e8e3e7", "accent": "#b7a6c9", "red": "#d43d55",
        "colors": ["#08080d", "#d43d55", "#75866f", "#b5a17b", "#586277", "#9b79a7", "#9eabb7", "#d2ccd2", "#282832", "#f05b6d", "#a2b58d", "#d2bd94", "#78839b", "#bd98c9", "#c9d4dc", "#f7f2f5"],
    },
    "light": {
        "background": "#e8e3e5", "foreground": "#17141b", "accent": "#655274", "red": "#a3263e",
        "colors": ["#e8e3e5", "#a3263e", "#4b614c", "#725c35", "#3f4d68", "#684775", "#435b68", "#332d35", "#a7a0a8", "#bd3851", "#617b60", "#92794a", "#5d6d8b", "#855d92", "#587280", "#17141b"],
    },
}

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _lum(hx):
    hx = hx.lstrip('#')
    r, g, b = (int(hx[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def _ratio(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def muted(dim, bg, fg, target=3.0):
    """ANSI color 8 is too dark/light to read as comment text on most of these
    palettes. Blend it toward the foreground until it clears `target` contrast
    against the background, preserving the palette's own hue."""
    if _ratio(dim, bg) >= target:
        return dim
    d = [int(dim.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    f = [int(fg.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    best = dim
    for step in range(1, 101):
        t = step / 100.0
        cand = '#%02x%02x%02x' % tuple(int(round(d[i] + (f[i] - d[i]) * t)) for i in range(3))
        best = cand
        if _ratio(cand, bg) >= target:
            break
    return best

def rgb(hex_color):
    return tuple(int(hex_color[i:i+2], 16) / 255 for i in (1, 3, 5))

def colors_toml(p):
    lines = [f'mode = "{p["mode"]}"', "", f'background = "{p["background"]}"', f'foreground = "{p["foreground"]}"', "", f'accent = "{p["accent"]}"', f'red     = "{p["red"]}"', ""]
    lines += [f'color{i:<2} = "{value}"' for i, value in enumerate(p["colors"])]
    return "\n".join(lines) + "\n"

def ghostty(p):
    return "\n".join([f"background = {p['background']}", f"foreground = {p['foreground']}", f"cursor-color = {p['accent']}", f"selection-background = {p['accent']}", *[f"palette = {i}={v}" for i, v in enumerate(p['colors'])]]) + "\n"

def kitty(p):
    return "\n".join([f"foreground {p['foreground']}", f"background {p['background']}", f"cursor {p['accent']}", f"selection_foreground {p['background']}", f"selection_background {p['accent']}", *[f"color{i} {v}" for i, v in enumerate(p['colors'])]]) + "\n"

def alacritty(p):
    c = p["colors"]
    names = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    return "[colors.primary]\nbackground = '" + p["background"] + "'\nforeground = '" + p["foreground"] + "'\n\n[colors.cursor]\ntext = '" + p["background"] + "'\ncursor = '" + p["accent"] + "'\n\n[colors.normal]\n" + "\n".join(f"{name} = '{value}'" for name, value in zip(names, c[:8])) + "\n\n[colors.bright]\n" + "\n".join(f"{name} = '{value}'" for name, value in zip(names, c[8:])) + "\n"

def wezterm(p):
    c = p["colors"]
    return "return {\n  foreground = '" + p["foreground"] + "',\n  background = '" + p["background"] + "',\n  cursor_bg = '" + p["accent"] + "',\n  cursor_fg = '" + p["background"] + "',\n  ansi = {" + ", ".join(repr(v) for v in c[:8]) + "},\n  brights = {" + ", ".join(repr(v) for v in c[8:]) + "},\n}\n"

def windows_terminal(p):
    c = p["colors"]
    return json.dumps({"name": "Neon Mary: The Crow (1994)", "background": p["background"], "foreground": p["foreground"], "cursorColor": p["accent"], "black": c[0], "red": c[1], "green": c[2], "yellow": c[3], "blue": c[4], "purple": c[5], "cyan": c[6], "white": c[7], "brightBlack": c[8], "brightRed": c[9], "brightGreen": c[10], "brightYellow": c[11], "brightBlue": c[12], "brightPurple": c[13], "brightCyan": c[14], "brightWhite": c[15]}, indent=2) + "\n"

def hermes_skin(p, mode):
    c = p["colors"]
    dim = muted(c[8], p["background"], p["foreground"])
    return f'''name: neon-mary-crow-{mode}
description: "Neon Mary: The Crow (1994) — gothic charcoal, ash, mauve, and blood red ({mode})."
colors:
  background: '{p["background"]}'
  status_bar_bg: '{p["background"]}'
  ui_accent: '{p["accent"]}'
  banner_accent: '{p["accent"]}'
  prompt: '{p["accent"]}'
  input_rule: '{p["red"]}'
  banner_title: '{c[14]}'
  ui_primary: '{c[14]}'
  session_label: '{c[14]}'
  response_border: '{c[6]}'
  banner_text: '{p["foreground"]}'
  ui_text: '{p["foreground"]}'
  ui_label: '{c[7]}'
  banner_dim: '{dim}'
  banner_border: '{c[6]}'
  ui_border: '{c[6]}'
  session_border: '{c[6]}'
  ui_tool: '{c[2]}'
  ui_thinking: '{c[5]}'
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
  syntax_keyword: '{c[14]}'
  syntax_comment: '{dim}'
  completion_menu_bg: '{p["background"]}'
  completion_menu_current_bg: '{c[6]}'
  completion_menu_meta_bg: '{p["background"]}'
branding:
  agent_name: Hermes Agent
  prompt_symbol: ❯
  welcome: It can't rain all the time.
  goodbye: Nothing is trivial.
  help_header: "◤ Neon Mary: The Crow — Commands"
spinner:
  waiting_faces: ["(◉)", "(◎)", "(⊙)"]
  thinking_faces: ["(⌁)", "(⊹)"]
  thinking_verbs: [watching, remembering, returning]
  wings: [["⟪◤", "◥⟫"], ["⟪△", "△⟫"]]
tool_prefix: ┊
'''

def wallpaper(source, out, width, height, mode):
    out.parent.mkdir(parents=True, exist_ok=True)
    grade = ["-modulate", "78,68,100"] if mode == "dark" else ["-modulate", "104,28,100"]
    if width == 3840 and height == 2160:
        command = ["magick", str(source), "-resize", "3840x2160^", "-gravity", "center", "-extent", "3840x2160", *grade, str(out)]
    else:
        command = ["magick", str(ROOT / "wallpapers" / mode / "4k.png"), "-resize", f"{width}x{height}^", "-gravity", "center", "-extent", f"{width}x{height}", str(out)]
    subprocess.run(command, check=True)

def main():
    if not SOURCE.exists():
        raise SystemExit(f"Missing source: {SOURCE}")
    for mode, base in PALETTES.items():
        p = dict(base); p["mode"] = mode
        (ROOT / "palettes").mkdir(exist_ok=True)
        write(ROOT / "palettes" / f"crow-{mode}.json", json.dumps(p, indent=2) + "\n")
        write(ROOT / "hermes" / "skins" / f"neon-mary-crow-{mode}.yaml", hermes_skin(p, mode))
        omarchy = ROOT / "omarchy" / "themes" / f"neon-mary-crow-{mode}"
        (omarchy / "backgrounds").mkdir(parents=True, exist_ok=True)
        write(omarchy / "colors.toml", colors_toml(p)); write(omarchy / "icons.theme", "Yaru-blue\n")
        for target, content in {"ghostty.conf": ghostty(p), "kitty.conf": kitty(p), "alacritty.toml": alacritty(p), "wezterm.lua": wezterm(p), "windows-terminal.json": windows_terminal(p)}.items():
            write(ROOT / "terminals" / "crow" / mode / target, content)
        write(ROOT / "terminals" / "crow" / mode / "fzf.conf", f"--color=bg:{p['background']},fg:{p['foreground']},hl:{p['accent']},border:{p['accent']},prompt:{p['accent']},pointer:{p['red']}\n")
        write(ROOT / "terminals" / "crow" / mode / "iterm2.json", json.dumps({"Name": f"Neon Mary: The Crow (1994) {mode}", "Background Color": dict(zip(("Red Component", "Green Component", "Blue Component"), rgb(p["background"]))), "Foreground Color": dict(zip(("Red Component", "Green Component", "Blue Component"), rgb(p["foreground"])))}, indent=2) + "\n")
        write(ROOT / "terminals" / "crow" / mode / "Terminal.app.terminal", json.dumps({"name": f"Neon Mary: The Crow (1994) {mode}", "profile": "Neon Mary: The Crow (1994)", "colors": p["colors"]}, indent=2) + "\n")
        write(ROOT / "editors" / "crow" / mode / "vscode-color-theme.json", json.dumps({"name": f"Neon Mary: The Crow (1994) {mode}", "type": mode, "colors": {"editor.background": p["background"], "editor.foreground": p["foreground"], "terminal.ansiCyan": p["colors"][6], "terminal.ansiMagenta": p["colors"][5], "terminal.ansiRed": p["red"], "terminal.ansiGreen": p["colors"][2]}, "tokenColors": []}, indent=2) + "\n")
        write(ROOT / "editors" / "crow" / mode / "vim.vim", f'" Neon Mary: The Crow (1994) {mode} palette\nlet g:neon_mary_crow_background = "{p["background"]}"\nlet g:neon_mary_crow_foreground = "{p["foreground"]}"\n')
        write(ROOT / "editors" / "crow" / mode / "tmux.conf", f'set -g status-style "bg={p["background"]},fg={p["foreground"]}"\nset -g pane-active-border-style "fg={p["accent"]}"\nset -g message-style "bg={p["background"]},fg={p["accent"]}"\n')
        for name, (width, height) in RESOLUTIONS.items():
            out = ROOT / "wallpapers" / "crow" / mode / f"{name}.png"
            wallpaper(SOURCE, out, width, height, mode)
            shutil.copy2(out, omarchy / "backgrounds" / f"{name}.png")
    write(ROOT / "omarchy" / "crow-README.md", """# Neon Mary: The Crow (1994)\n\nNeon Mary is the theme family; `neon-mary-crow-{dark,light}` are the gothic Crow (1994) variant's native Omarchy packages. `apply-crow.sh` installs the selected package, applies the 4K wallpaper, refreshes shell IPC, and enables the transparent top bar.\n\n```sh\n./omarchy/apply-crow.sh dark\n```\n""")

if __name__ == "__main__":
    main()
