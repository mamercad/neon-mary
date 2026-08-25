#!/usr/bin/env python3
"""Generate the Neon Mary: Neon Genesis Evangelion (1995) variant."""
from pathlib import Path
import json
import shutil
import subprocess

from palette_utils import light_grade_args, muted, pick

ROOT = Path(__file__).resolve().parent
SOURCE = Path.home() / "Pictures" / "mary.png"
RESOLUTIONS = {"4k": (3840, 2160), "wqhd": (2560, 1440), "qhd": (1920, 1080), "16-10": (2560, 1600), "3-2": (2160, 1440), "4-3": (2048, 1536), "1-1": (2048, 2048), "9-16": (1440, 2560)}
PALETTES = {
    "dark": {"background":"#120d18", "foreground":"#f4f3e8", "accent":"#a976c3", "red":"#d3290f", "colors":["#120d18","#d3290f","#a0de59","#f5c024","#466b5a","#5f2a62","#a976c3","#f4f3e8","#34233b","#f04b2f","#c1f47b","#ffe36a","#6e9b83","#bb8dd4","#cba9dc","#fffdf2"]},
    # Light mode inverts to bone-white with the accents darkened. Note c[5]
    # is deliberately a deeper plum than `accent`: both were #663873, which
    # made the showcase legend advertise "accent" and "alt" as two colours
    # while rendering one indistinguishable pair of swatches.
    "light": {"background":"#f2ecdf", "foreground":"#241a28", "accent":"#663873", "red":"#a52212", "colors":["#f2ecdf","#a52212","#4f7728","#8a6500","#285246","#4a2154","#4c7890","#241a28","#bcaeae","#c23825","#70983c","#aa8615","#4b7980","#875393","#5c8da2","#241a28"]},
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

def windows(p, mode):
    c = p["colors"]; names = ["black", "red", "green", "yellow", "blue", "purple", "cyan", "white"]
    data = {"name":f"Neon Mary: Neon Genesis Evangelion (1995) {mode}","background":p["background"],"foreground":p["foreground"],"cursorColor":p["accent"]}
    data.update(dict(zip(names, c[:8]))); data.update(dict(zip(["bright" + n.title() for n in names], c[8:])))
    return json.dumps(data, indent=2) + "\n"

def hermes(p, mode):
    c = p["colors"]
    # ANSI 8 sits far too close to the background to read as comment text
    # (1.32:1 dark, 1.82:1 light here). Blend toward the foreground until it
    # clears 3:1 while keeping the palette's own hue.
    dim = muted(c[8], p["background"], p["foreground"])
    # ANSI 5 here is a deep Unit-01 aubergine (1.82:1 dark); fall back to its
    # bright counterpart, which is the same hue and clears 7:1.
    thinking = pick(p["background"], p["foreground"], c[5], c[13])
    return f'''name: neon-mary-evangelion-{mode}
description: "Neon Mary: Neon Genesis Evangelion (1995) — Unit-01 purple, toxic green, signal orange, and NERV black ({mode})."
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
  ui_thinking: '{thinking}'
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
  welcome: God’s in his heaven. All’s right with the world.
  goodbye: Congratulations!
  help_header: "◤ Neon Mary: Evangelion — Commands"
spinner:
  waiting_faces: ["(◉)", "(◎)", "(⊙)"]
  thinking_faces: ["(⌁)", "(⊹)"]
  thinking_verbs: [synchronizing, deploying, analyzing]
  wings: [["⟪◤", "◥⟫"], ["⟪△", "△⟫"]]
tool_prefix: ┊
'''

def wallpaper(source, out, width, height, mode):
    out.parent.mkdir(parents=True, exist_ok=True)
    is4k = (width, height) == (3840, 2160)
    base = source if is4k else ROOT / "wallpapers" / "evangelion" / mode / "4k.png"
    # Grade only on the 4k pass; the other sizes are resized from the already
    # graded 4k, so re-applying would double-process them.
    if not is4k:
        grade = []
    elif mode == "dark":
        grade = ["-modulate", "86,78,100"]
    else:
        # -modulate is a gain and cannot lift this dark a source into a real
        # light mode; use the shared tonal remap, tinted with the light bg.
        grade = light_grade_args(PALETTES["light"]["background"])
    subprocess.run(["magick", str(base), "-resize", f"{width}x{height}^", "-gravity", "center", "-extent", f"{width}x{height}", *grade, str(out)], check=True)

def main():
    if not SOURCE.exists(): raise SystemExit(f"Missing source: {SOURCE}")
    for mode, base in PALETTES.items():
        p = dict(base); p["mode"] = mode
        write(ROOT / "palettes" / f"evangelion-{mode}.json", json.dumps(p, indent=2) + "\n")
        write(ROOT / "hermes" / "skins" / f"neon-mary-evangelion-{mode}.yaml", hermes(p, mode))
        om = ROOT / "omarchy" / "themes" / f"neon-mary-evangelion-{mode}"
        (om / "backgrounds").mkdir(parents=True, exist_ok=True)
        write(om / "colors.toml", colors_toml(p)); write(om / "icons.theme", "Yaru-blue\n")
        exports = {"ghostty.conf":ghostty(p),"kitty.conf":kitty(p),"alacritty.toml":alacritty(p),"wezterm.lua":wezterm(p),"windows-terminal.json":windows(p, mode),"fzf.conf":f"--color=bg:{p['background']},fg:{p['foreground']},hl:{p['accent']},border:{p['accent']},prompt:{p['accent']},pointer:{p['red']}\n","iterm2.json":json.dumps({"Name":f"Neon Mary: Neon Genesis Evangelion (1995) {mode}","Background Color":dict(zip(("Red Component","Green Component","Blue Component"),rgb(p["background"]))),"Foreground Color":dict(zip(("Red Component","Green Component","Blue Component"),rgb(p["foreground"])))},indent=2)+"\n","Terminal.app.terminal":json.dumps({"name":f"Neon Mary: Neon Genesis Evangelion (1995) {mode}","profile":"Neon Mary: Neon Genesis Evangelion (1995)","colors":p["colors"]},indent=2)+"\n"}
        for name, content in exports.items(): write(ROOT / "terminals" / "evangelion" / mode / name, content)
        write(ROOT / "editors" / "evangelion" / mode / "vscode-color-theme.json", json.dumps({"name":f"Neon Mary: Neon Genesis Evangelion (1995) {mode}","type":mode,"colors":{"editor.background":p["background"],"editor.foreground":p["foreground"],"terminal.ansiCyan":p["colors"][6],"terminal.ansiMagenta":p["colors"][5],"terminal.ansiRed":p["red"],"terminal.ansiGreen":p["colors"][2]},"tokenColors":[]},indent=2)+"\n")
        write(ROOT / "editors" / "evangelion" / mode / "vim.vim", f'" Neon Mary: Neon Genesis Evangelion (1995) {mode} palette\nlet g:neon_mary_evangelion_background = "{p["background"]}"\nlet g:neon_mary_evangelion_foreground = "{p["foreground"]}"\n')
        write(ROOT / "editors" / "evangelion" / mode / "tmux.conf", f'set -g status-style "bg={p["background"]},fg={p["foreground"]}"\nset -g pane-active-border-style "fg={p["accent"]}"\nset -g message-style "bg={p["background"]},fg={p["accent"]}"\n')
        for name, (width, height) in RESOLUTIONS.items():
            out = ROOT / "wallpapers" / "evangelion" / mode / f"{name}.png"
            wallpaper(SOURCE, out, width, height, mode)
            shutil.copy2(out, om / "backgrounds" / f"{name}.png")
    write(ROOT / "omarchy" / "evangelion-README.md", "# Neon Mary: Neon Genesis Evangelion (1995)\n\nNeon Mary is the theme family; these are the Neon Genesis Evangelion variant native Omarchy packages.\n")

if __name__ == "__main__": main()
