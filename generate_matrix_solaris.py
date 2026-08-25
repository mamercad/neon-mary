#!/usr/bin/env python3
"""Generate the Neon Mary: Matrix (1999) and Solaris (1972) variants."""
from pathlib import Path
import json, shutil, subprocess
from palette_utils import muted, light_grade_args

ROOT = Path(__file__).resolve().parent
SOURCE = Path.home() / "Pictures" / "mary.png"
RESOLUTIONS = {"4k": (3840,2160), "wqhd": (2560,1440), "qhd": (1920,1080), "16-10": (2560,1600), "3-2": (2160,1440), "4-3": (2048,1536), "1-1": (2048,2048), "9-16": (1440,2560)}
VARIANTS = {
    "matrix": {
        "title": "The Matrix (1999)", "tagline": "THERE IS NO SPOON.",
        "caption": "phosphor green / constructed world",
        "dark": {"background":"#07120b", "foreground":"#d9ffe1", "accent":"#39ff88", "red":"#ff5c62", "colors":["#07120b","#ff5c62","#39d353","#d7d34e","#318b58","#9a7cff","#39ff88","#d9ffe1","#1b3d27","#ff8589","#78ff9d","#f2ef78","#61bd82","#b9a7ff","#8affb8","#f2fff4"]},
        "light": {"background":"#edf7ef", "foreground":"#102318", "accent":"#168f4d", "red":"#b52e3a", "colors":["#edf7ef","#b52e3a","#267b3f","#806d00","#21633e","#684b9a","#168f4d","#102318","#a9c5ae","#cf4d58","#4d995e","#a08c00","#458e61","#8064ad","#3a9d61","#102318"]},
    },
    "solaris": {
        "title": "Solaris (1972)", "tagline": "THE OCEAN REMEMBERS.",
        "caption": "amber instrument light / distant ocean",
        "dark": {"background":"#17130e", "foreground":"#fff2d2", "accent":"#d7a84b", "red":"#d45a4f", "colors":["#17130e","#d45a4f","#7c9a63","#d7a84b","#597896","#9b718f","#d7a84b","#fff2d2","#493b2a","#ed7964","#a6bc83","#f0cc72","#82a4c3","#c095b1","#f1c76c","#fffaf0"]},
        "light": {"background":"#f5eedf", "foreground":"#2c2418", "accent":"#9c6a18", "red":"#a63e36", "colors":["#f5eedf","#a63e36","#4e713b","#9c6a18","#3c607a","#76506d","#9c6a18","#2c2418","#c9bca6","#c45b4f","#729559","#bd8d28","#6387a2","#98728e","#76500f","#2c2418"]},
    },
}

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8")
def rgb(h): return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def colors_toml(p):
    lines=[f'mode = "{p["mode"]}"','',f'background = "{p["background"]}"',f'foreground = "{p["foreground"]}"','',f'accent = "{p["accent"]}"',f'red     = "{p["red"]}"','']
    return "\n".join(lines+[f'color{i:<2} = "{v}"' for i,v in enumerate(p["colors"])])+"\n"
def ghostty(p): return "\n".join([f"background = {p['background']}",f"foreground = {p['foreground']}",f"cursor-color = {p['accent']}",f"selection-background = {p['accent']}",*[f"palette = {i}={v}" for i,v in enumerate(p['colors'])]])+"\n"
def kitty(p): return "\n".join([f"foreground {p['foreground']}",f"background {p['background']}",f"cursor {p['accent']}",f"selection_foreground {p['background']}",f"selection_background {p['accent']}",*[f"color{i} {v}" for i,v in enumerate(p['colors'])]])+"\n"
def alacritty(p):
    c=p["colors"]; names=['black','red','green','yellow','blue','magenta','cyan','white']
    return "[colors.primary]\nbackground = '"+p['background']+"'\nforeground = '"+p['foreground']+"'\n\n[colors.cursor]\ntext = '"+p['background']+"'\ncursor = '"+p['accent']+"'\n\n[colors.normal]\n"+"\n".join(f"{n} = '{v}'" for n,v in zip(names,c[:8]))+"\n\n[colors.bright]\n"+"\n".join(f"{n} = '{v}'" for n,v in zip(names,c[8:]))+"\n"
def wezterm(p):
    c=p['colors']; return "return {\n  foreground = '"+p['foreground']+"',\n  background = '"+p['background']+"',\n  cursor_bg = '"+p['accent']+"',\n  cursor_fg = '"+p['background']+"',\n  ansi = {"+", ".join(repr(v) for v in c[:8])+"},\n  brights = {"+", ".join(repr(v) for v in c[8:])+"},\n}\n"
def windows(p, title, mode):
    c=p['colors']; names=['black','red','green','yellow','blue','purple','cyan','white']; d={"name":f"Neon Mary: {title} {mode}","background":p['background'],"foreground":p['foreground'],"cursorColor":p['accent']}; d.update(dict(zip(names,c[:8]))); d.update(dict(zip(['bright'+n.title() for n in names],c[8:]))); return json.dumps(d,indent=2)+"\n"
def vscode(p,title,mode): return json.dumps({"name":f"Neon Mary: {title} {mode}","type":mode,"colors":{"editor.background":p['background'],"editor.foreground":p['foreground'],"terminal.ansiCyan":p['colors'][6],"terminal.ansiMagenta":p['colors'][5],"terminal.ansiRed":p['red'],"terminal.ansiGreen":p['colors'][2]},"tokenColors":[]},indent=2)+"\n"
def hermes(p,tag,title,mode):
    c=p['colors']; dim=muted(c[8],p['background'],p['foreground'])
    return f'''name: neon-mary-{tag}-{mode}
description: "Neon Mary: {title} — {('phosphor green and constructed reality' if tag == 'matrix' else 'amber instruments and the remembered ocean')} ({mode})."
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
  ui_thinking: '{c[5]}'
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
  welcome: {"Wake up, Neo." if tag == "matrix" else "We are not on Earth."}
  goodbye: {"There is no spoon." if tag == "matrix" else "The ocean remembers."}
  help_header: "◤ Neon Mary: {title} — Commands"
spinner:
  waiting_faces: ["(◉)", "(◎)", "(⊙)"]
  thinking_faces: ["(⌁)", "(⊹)"]
  thinking_verbs: ["tracing", "decoding", "observing"]
  wings: [["⟪◤", "◥⟫"], ["⟪△", "△⟫"]]
tool_prefix: ┊
'''
def wallpaper(tag,p,mode,out,w,h):
    is4k=(w,h)==(3840,2160); base=SOURCE if is4k else ROOT/'wallpapers'/tag/mode/'4k.png'; grade=[] if not is4k else (["-modulate","82,78,100","-fill",p['accent'],"-colorize","24"] if tag=="matrix" and mode=="dark" else ["-modulate","82,78,100"] if mode=="dark" else light_grade_args(p['background']))
    out.parent.mkdir(parents=True,exist_ok=True); subprocess.run(["magick",str(base),"-resize",f"{w}x{h}^","-gravity","center","-extent",f"{w}x{h}",*grade,str(out)],check=True)
def main():
    if not SOURCE.exists(): raise SystemExit(f"Missing source: {SOURCE}")
    for tag,v in VARIANTS.items():
        for mode,base in (("dark",v['dark']),("light",v['light'])):
            p=dict(base,mode=mode); stem=f"neon-mary-{tag}-{mode}"; write(ROOT/'palettes'/f'{tag}-{mode}.json',json.dumps(p,indent=2)+'\n'); write(ROOT/'hermes'/'skins'/f'{stem}.yaml',hermes(p,tag,v['title'],mode))
            om=ROOT/'omarchy'/'themes'/stem; (om/'backgrounds').mkdir(parents=True, exist_ok=True); write(om/'colors.toml',colors_toml(p)); write(om/'icons.theme','Yaru-blue\n')
            targets={'ghostty.conf':ghostty(p),'kitty.conf':kitty(p),'alacritty.toml':alacritty(p),'wezterm.lua':wezterm(p),'windows-terminal.json':windows(p,v['title'],mode),'fzf.conf':f"--color=bg:{p['background']},fg:{p['foreground']},hl:{p['accent']},border:{p['accent']},prompt:{p['accent']},pointer:{p['red']}\n",'iterm2.json':json.dumps({'Name':f"Neon Mary: {v['title']} {mode}",'Background Color':dict(zip(('Red Component','Green Component','Blue Component'),rgb(p['background']))),'Foreground Color':dict(zip(('Red Component','Green Component','Blue Component'),rgb(p['foreground'])))},indent=2)+'\n','Terminal.app.terminal':json.dumps({'name':f"Neon Mary: {v['title']} {mode}",'profile':f"Neon Mary: {v['title']}",'colors':p['colors']},indent=2)+'\n'}
            for name,text in targets.items(): write(ROOT/'terminals'/tag/mode/name,text)
            write(ROOT/'editors'/tag/mode/'vscode-color-theme.json',vscode(p,v['title'],mode)); write(ROOT/'editors'/tag/mode/'vim.vim',f'" Neon Mary: {v["title"]} {mode} palette\nlet g:neon_mary_{tag}_background = "{p["background"]}"\nlet g:neon_mary_{tag}_foreground = "{p["foreground"]}"\n'); write(ROOT/'editors'/tag/mode/'tmux.conf',f'set -g status-style "bg={p["background"]},fg={p["foreground"]}"\nset -g pane-active-border-style "fg={p["accent"]}"\nset -g message-style "bg={p["background"]},fg={p["accent"]}"\n')
            for name,(w,h) in RESOLUTIONS.items():
                out=ROOT/'wallpapers'/tag/mode/f'{name}.png'; wallpaper(tag,p,mode,out,w,h); shutil.copy2(out,om/'backgrounds'/f'{name}.png')
        write(ROOT/'omarchy'/f'{tag}-README.md',f"# Neon Mary: {v['title']}\n\nNeon Mary is the theme family; these are the {v['title']} variant native Omarchy packages.\n")
if __name__=='__main__': main()
