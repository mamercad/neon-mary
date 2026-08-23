#!/usr/bin/env python3
"""Generate the Neon Mary: Tron (1982) variant."""
from pathlib import Path
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCE = Path.home() / "Pictures" / "mary.png"
RESOLUTIONS = {"4k": (3840, 2160), "wqhd": (2560, 1440), "qhd": (1920, 1080), "16-10": (2560, 1600), "3-2": (2160, 1440), "4-3": (2048, 1536), "1-1": (2048, 2048), "9-16": (1440, 2560)}
PALETTES = {
    "dark": {"background":"#050b12", "foreground":"#d9f7ff", "accent":"#00c8ff", "red":"#ff4b36", "colors":["#050b12","#ff4b36","#61d36e","#e7c34f","#147aa0","#8b6cff","#00c8ff","#d9f7ff","#18303e","#ff735f","#8bec91","#ffe477","#42b7dc","#b19dff","#62e4ff","#f3fdff"]},
    "light": {"background":"#e5f1f3", "foreground":"#10252d", "accent":"#007b9c", "red":"#b32e2a", "colors":["#e5f1f3","#b32e2a","#26703a","#856900","#17526e","#5e4388","#007b9c","#10252d","#9dbbc2","#cf493c","#438450","#a28600","#347b94","#8060a8","#198aa4","#10252d"]},
}

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)

def rgb(value):
    return tuple(int(value[i:i+2], 16) / 255 for i in (1, 3, 5))

def colors_toml(p):
    lines = [f'mode = "{p["mode"]}"', "", f'background = "{p["background"]}"', f'foreground = "{p["foreground"]}"', "", f'accent = "{p["accent"]}"', f'red     = "{p["red"]}"', ""]
    return "\n".join(lines + [f'color{i:<2} = "{v}"' for i, v in enumerate(p["colors"])]) + "\n"

def ghostty(p):
    return "\n".join([f"background = {p['background']}", f"foreground = {p['foreground']}", f"cursor-color = {p['accent']}", f"selection-background = {p['accent']}", *[f"palette = {i}={v}" for i, v in enumerate(p['colors'])]]) + "\n"

def kitty(p):
    return "\n".join([f"foreground {p['foreground']}", f"background {p['background']}", f"cursor {p['accent']}", f"selection_foreground {p['background']}", f"selection_background {p['accent']}", *[f"color{i} {v}" for i, v in enumerate(p['colors'])]]) + "\n"

def alacritty(p):
    c = p["colors"]; names = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    return "[colors.primary]\nbackground = '" + p["background"] + "'\nforeground = '" + p["foreground"] + "'\n\n[colors.cursor]\ntext = '" + p["background"] + "'\ncursor = '" + p["accent"] + "'\n\n[colors.normal]\n" + "\n".join(f"{n} = '{v}'" for n, v in zip(names, c[:8])) + "\n\n[colors.bright]\n" + "\n".join(f"{n} = '{v}'" for n, v in zip(names, c[8:])) + "\n"

def wezterm(p):
    c = p["colors"]
    return "return {\n  foreground = '" + p["foreground"] + "',\n  background = '" + p["background"] + "',\n  cursor_bg = '" + p["accent"] + "',\n  cursor_fg = '" + p["background"] + "',\n  ansi = {" + ", ".join(repr(v) for v in c[:8]) + "},\n  brights = {" + ", ".join(repr(v) for v in c[8:]) + "},\n}\n"

def windows(p):
    c = p["colors"]
    names = ["black", "red", "green", "yellow", "blue", "purple", "cyan", "white"]
    data = {"name": "Neon Mary: Tron (1982)", "background": p["background"], "foreground": p["foreground"], "cursorColor": p["accent"]}
    data.update(dict(zip(names, c[:8]))); data.update(dict(zip(["bright" + n.title() for n in names], c[8:])))
    return json.dumps(data, indent=2) + "\n"

def hermes(p, mode):
    c = p["colors"]
    return f'''name: neon-mary-tron-{mode}
description: "Neon Mary: Tron (1982) — electric cyan, phosphor blue, amber, and grid black ({mode})."
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
  banner_dim: '{c[8]}'
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
  syntax_comment: '{c[8]}'
  completion_menu_bg: '{p["background"]}'
  completion_menu_current_bg: '{c[6]}'
  completion_menu_meta_bg: '{p["background"]}'
branding:
  agent_name: Hermes Agent
  prompt_symbol: ❯
  welcome: The grid is open.
  goodbye: End of line.
  help_header: "◤ Neon Mary: Tron — Commands"
spinner:
  waiting_faces: ["(◉)", "(◎)", "(⊙)"]
  thinking_faces: ["(⌁)", "(⊹)"]
  thinking_verbs: [compiling, derezzing, traversing]
  wings: [["⟪◤", "◥⟫"], ["⟪△", "△⟫"]]
tool_prefix: ┊
'''

def wallpaper(source, out, width, height, mode):
    grade = ["-modulate", "88,82,100"] if mode == "dark" else ["-modulate", "106,48,100"]
    base = source if (width, height) == (3840, 2160) else ROOT / "wallpapers" / "tron" / mode / "4k.png"
    subprocess.run(["magick", str(base), "-resize", f"{width}x{height}^", "-gravity", "center", "-extent", f"{width}x{height}", *grade, str(out)], check=True)

def main():
    if not SOURCE.exists(): raise SystemExit(f"Missing source: {SOURCE}")
    for mode, base in PALETTES.items():
        p = dict(base); p["mode"] = mode
        write(ROOT / "palettes" / f"tron-{mode}.json", json.dumps(p, indent=2) + "\n")
        write(ROOT / "hermes" / "skins" / f"neon-mary-tron-{mode}.yaml", hermes(p, mode))
        om = ROOT / "omarchy" / "themes" / f"neon-mary-tron-{mode}"; (om / "backgrounds").mkdir(parents=True, exist_ok=True)
        write(om / "colors.toml", colors_toml(p)); write(om / "icons.theme", "Yaru-blue\n")
        targets = {"ghostty.conf": ghostty(p), "kitty.conf": kitty(p), "alacritty.toml": alacritty(p), "wezterm.lua": wezterm(p), "windows-terminal.json": windows(p), "fzf.conf": f"--color=bg:{p['background']},fg:{p['foreground']},hl:{p['accent']},border:{p['accent']},prompt:{p['accent']},pointer:{p['red']}\n", "iterm2.json": json.dumps({"Name": f"Neon Mary: Tron (1982) {mode}", "Background Color": dict(zip(("Red Component", "Green Component", "Blue Component"), rgb(p["background"]))), "Foreground Color": dict(zip(("Red Component", "Green Component", "Blue Component"), rgb(p["foreground"])))}, indent=2) + "\n", "Terminal.app.terminal": json.dumps({"name": f"Neon Mary: Tron (1982) {mode}", "profile": "Neon Mary: Tron (1982)", "colors": p["colors"]}, indent=2) + "\n"}
        for name, content in targets.items(): write(ROOT / "terminals" / "tron" / mode / name, content)
        write(ROOT / "editors" / "tron" / mode / "vscode-color-theme.json", json.dumps({"name": f"Neon Mary: Tron (1982) {mode}", "type": mode, "colors": {"editor.background": p["background"], "editor.foreground": p["foreground"], "terminal.ansiCyan": p["colors"][6], "terminal.ansiMagenta": p["colors"][5], "terminal.ansiRed": p["red"], "terminal.ansiGreen": p["colors"][2]}, "tokenColors": []}, indent=2) + "\n")
        write(ROOT / "editors" / "tron" / mode / "vim.vim", f'" Neon Mary: Tron (1982) {mode} palette\nlet g:neon_mary_tron_background = "{p["background"]}"\nlet g:neon_mary_tron_foreground = "{p["foreground"]}"\n')
        write(ROOT / "editors" / "tron" / mode / "tmux.conf", f'set -g status-style "bg={p["background"]},fg={p["foreground"]}"\nset -g pane-active-border-style "fg={p["accent"]}"\nset -g message-style "bg={p["background"]},fg={p["accent"]}"\n')
        for name, (width, height) in RESOLUTIONS.items():
            out = ROOT / "wallpapers" / "tron" / mode / f"{name}.png"; out.parent.mkdir(parents=True, exist_ok=True); wallpaper(SOURCE, out, width, height, mode); shutil.copy2(out, om / "backgrounds" / f"{name}.png")
    write(ROOT / "omarchy" / "tron-README.md", "# Neon Mary: Tron (1982)\n\nNeon Mary is the theme family; these are the Tron (1982) variant native Omarchy packages.\n")

if __name__ == "__main__": main()
