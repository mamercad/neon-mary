#!/usr/bin/env python3
"""Generate the Neon Mary: Suspiria (1977) variant."""
from pathlib import Path
import json, shutil, subprocess
from palette_utils import light_grade_args, muted, pick

ROOT = Path(__file__).resolve().parent
SOURCE = Path.home() / "Pictures" / "mary.png"
RESOLUTIONS = {"4k": (3840, 2160), "wqhd": (2560, 1440), "qhd": (1920, 1080), "16-10": (2560, 1600), "3-2": (2160, 1440), "4-3": (2048, 1536), "1-1": (2048, 2048), "9-16": (1440, 2560)}
PALETTES = {
    "dark": {"background":"#10070b", "foreground":"#fff1d6", "accent":"#e33b42", "red":"#ff4d5a", "colors":["#10070b","#ff4d5a","#d6d84a","#f2c230","#406bb3","#d12a78","#3f78cf","#fff1d6","#3c1820","#ff7a6e","#edf06f","#ffe36b","#6c98d6","#ee6b9e","#ff9c76","#fff8e8"]},
    "light": {"background":"#fff4df", "foreground":"#241116", "accent":"#a51f3c", "red":"#9f1729", "colors":["#fff4df","#9f1729","#58720d","#9b6900","#23558e","#7d204b","#1c5da8","#241116","#b28f8d","#c44343","#78942f","#b18416","#4776a9","#a34b76","#ad4b43","#241116"]},
}

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8")

def rgb(value): return tuple(int(value[i:i+2], 16) / 255 for i in (1, 3, 5))

def colors_toml(p):
    head = [f'mode = "{p["mode"]}"', "", f'background = "{p["background"]}"', f'foreground = "{p["foreground"]}"', "", f'accent = "{p["accent"]}"', f'red     = "{p["red"]}"', ""]
    return "\n".join(head + [f'color{i:<2} = "{v}"' for i, v in enumerate(p["colors"])]) + "\n"

def ghostty(p):
    return "\n".join([f"background = {p['background']}", f"foreground = {p['foreground']}", f"cursor-color = {p['accent']}", f"selection-background = {p['accent']}", *[f"palette = {i}={v}" for i, v in enumerate(p['colors'])]]) + "\n"

def kitty(p):
    return "\n".join([f"foreground {p['foreground']}", f"background {p['background']}", f"cursor {p['accent']}", f"selection_foreground {p['background']}", f"selection_background {p['accent']}", *[f"color{i} {v}" for i, v in enumerate(p['colors'])]]) + "\n"

def alacritty(p):
    c=p["colors"]; names=['black','red','green','yellow','blue','magenta','cyan','white']
    return "[colors.primary]\nbackground = '"+p['background']+"'\nforeground = '"+p['foreground']+"'\n\n[colors.cursor]\ntext = '"+p['background']+"'\ncursor = '"+p['accent']+"'\n\n[colors.normal]\n"+"\n".join(f"{n} = '{v}'" for n,v in zip(names,c[:8]))+"\n\n[colors.bright]\n"+"\n".join(f"{n} = '{v}'" for n,v in zip(names,c[8:]))+"\n"

def wezterm(p):
    c=p['colors']; return "return {\n  foreground = '"+p['foreground']+"',\n  background = '"+p['background']+"',\n  cursor_bg = '"+p['accent']+"',\n  cursor_fg = '"+p['background']+"',\n  ansi = {"+", ".join(repr(v) for v in c[:8])+"},\n  brights = {"+", ".join(repr(v) for v in c[8:])+"},\n}\n"

def windows(p, mode):
    c=p['colors']; names=['black','red','green','yellow','blue','purple','cyan','white']; d={"name":f"Neon Mary: Suspiria (1977) {mode}","background":p['background'],"foreground":p['foreground'],"cursorColor":p['accent']}; d.update(dict(zip(names,c[:8]))); d.update(dict(zip(['bright'+n.title() for n in names],c[8:]))); return json.dumps(d,indent=2)+"\n"

def hermes(p, mode):
    c=p['colors']; dim=muted(c[8],p['background'],p['foreground']); thinking=pick(p['background'],p['foreground'],c[5],c[13])
    return f'''name: neon-mary-suspiria-{mode}
description: "Neon Mary: Suspiria (1977) — blood red, cobalt blue, acid yellow, and theatrical black ({mode})."
colors:
  background: '{p['background']}'
  status_bar_bg: '{p['background']}'
  ui_accent: '{p['accent']}'
  banner_accent: '{p['accent']}'
  prompt: '{p['accent']}'
  input_rule: '{p['red']}'
  banner_title: '{c[14]}'
  ui_primary: '{c[14]}'
  session_label: '{c[14]}'
  response_border: '{c[6]}'
  banner_text: '{p['foreground']}'
  ui_text: '{p['foreground']}'
  ui_label: '{c[7]}'
  banner_dim: '{dim}'
  banner_border: '{c[6]}'
  ui_border: '{c[6]}'
  session_border: '{c[6]}'
  ui_tool: '{c[2]}'
  ui_thinking: '{thinking}'
  ui_ok: '{c[2]}'
  ui_warn: '{c[3]}'
  ui_error: '{p['red']}'
  status_bar_text: '{c[7]}'
  status_bar_good: '{c[2]}'
  status_bar_warn: '{c[3]}'
  status_bar_bad: '{c[9]}'
  status_bar_critical: '{p['red']}'
  syntax_string: '{c[2]}'
  syntax_number: '{c[3]}'
  syntax_keyword: '{c[14]}'
  syntax_comment: '{dim}'
  completion_menu_bg: '{p['background']}'
  completion_menu_current_bg: '{c[6]}'
  completion_menu_meta_bg: '{p['background']}'
branding:
  agent_name: Hermes Agent
  prompt_symbol: ❯
  welcome: The dance begins.
  goodbye: The red room is waiting.
  help_header: "◤ Neon Mary: Suspiria — Commands"
spinner:
  waiting_faces: ["(◉)", "(◎)", "(⊙)"]
  thinking_faces: ["(⌁)", "(⊹)"]
  thinking_verbs: ["rehearsing", "summoning", "observing"]
  wings: [["⟪◤", "◥⟫"], ["⟪△", "△⟫"]]
tool_prefix: ┊
'''

def wallpaper(out, width, height, mode):
    out.parent.mkdir(parents=True, exist_ok=True); is4k=(width,height)==(3840,2160); base=SOURCE if is4k else ROOT/'wallpapers'/'suspiria'/mode/'4k.png'
    grade=[] if not is4k else (["-modulate","88,82,100"] if mode=="dark" else light_grade_args(PALETTES["light"]["background"]))
    subprocess.run(["magick",str(base),"-resize",f"{width}x{height}^","-gravity","center","-extent",f"{width}x{height}",*grade,str(out)],check=True)

def main():
    if not SOURCE.exists(): raise SystemExit(f"Missing source: {SOURCE}")
    for mode, base in PALETTES.items():
        p=dict(base,mode=mode); om=ROOT/'omarchy'/'themes'/f'neon-mary-suspiria-{mode}'; (om/'backgrounds').mkdir(parents=True,exist_ok=True)
        write(ROOT/'palettes'/f'suspiria-{mode}.json',json.dumps(p,indent=2)+'\n'); write(ROOT/'hermes'/'skins'/f'neon-mary-suspiria-{mode}.yaml',hermes(p,mode)); write(om/'colors.toml',colors_toml(p)); write(om/'icons.theme','Yaru-blue\n')
        exports={'ghostty.conf':ghostty(p),'kitty.conf':kitty(p),'alacritty.toml':alacritty(p),'wezterm.lua':wezterm(p),'windows-terminal.json':windows(p,mode),'fzf.conf':f"--color=bg:{p['background']},fg:{p['foreground']},hl:{p['accent']},border:{p['accent']},prompt:{p['accent']},pointer:{p['red']}\n"}
        for name,text in exports.items(): write(ROOT/'terminals'/'suspiria'/mode/name,text)
        write(ROOT/'editors'/'suspiria'/mode/'vscode-color-theme.json',json.dumps({'name':f'Neon Mary: Suspiria (1977) {mode}','type':mode,'colors':{'editor.background':p['background'],'editor.foreground':p['foreground'],'terminal.ansiCyan':p['colors'][6],'terminal.ansiMagenta':p['colors'][5],'terminal.ansiRed':p['red'],'terminal.ansiGreen':p['colors'][2]},'tokenColors':[]},indent=2)+'\n')
        write(ROOT/'editors'/'suspiria'/mode/'vim.vim',f'" Neon Mary: Suspiria (1977) {mode} palette\nlet g:neon_mary_suspiria_background = "{p["background"]}"\nlet g:neon_mary_suspiria_foreground = "{p["foreground"]}"\n')
        write(ROOT/'editors'/'suspiria'/mode/'tmux.conf',f'set -g status-style "bg={p["background"]},fg={p["foreground"]}"\nset -g pane-active-border-style "fg={p["accent"]}"\nset -g message-style "bg={p["background"]},fg={p["accent"]}"\n')
        for name,size in RESOLUTIONS.items():
            out=ROOT/'wallpapers'/'suspiria'/mode/f'{name}.png'; wallpaper(out,*size,mode); shutil.copy2(out,om/'backgrounds'/f'{name}.png')
    write(ROOT/'omarchy'/'suspiria-README.md','# Neon Mary: Suspiria (1977)\n\nNeon Mary is the theme family; these are the Suspiria variant native Omarchy packages.\n')

if __name__ == '__main__': main()
