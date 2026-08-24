#!/usr/bin/env python3
"""Generate the Neon Mary: Amélie (2001) variant."""
from pathlib import Path
import json
import shutil
import subprocess

from palette_utils import muted, light_grade_args

ROOT = Path(__file__).resolve().parent
SOURCE = Path.home() / "Pictures" / "mary.png"
RESOLUTIONS = {"4k": (3840, 2160), "wqhd": (2560, 1440), "qhd": (1920, 1080), "16-10": (2560, 1600), "3-2": (2160, 1440), "4-3": (2048, 1536), "1-1": (2048, 2048), "9-16": (1440, 2560)}
PALETTES = {
    "dark": {"background":"#17120f", "foreground":"#fff0d8", "accent":"#d95b32", "red":"#b8322d", "colors":["#17120f","#b8322d","#7b8b32","#c9972b","#315f68","#b84b2f","#4c8f8b","#fff0d8","#49362c","#df5b4c","#a6ad4e","#f0bd3e","#4b8791","#d46a4c","#70b7ae","#fff7e9"]},
    "light": {"background":"#f8ead2", "foreground":"#2c1c18", "accent":"#b83f26", "red":"#972c28", "colors":["#f8ead2","#972c28","#596b25","#9a6d13","#24525b","#933a26","#26716d","#3c2921","#c6ab88","#b83f26","#71852e","#b1811e","#3c7379","#ae5238","#398b83","#2c1c18"]},
}

def write(path, text): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text)
def rgb(value): return tuple(int(value[i:i+2],16)/255 for i in (1,3,5))


def toml(p):
    lines=[f'mode = "{p["mode"]}"',"",f'background = "{p["background"]}"',f'foreground = "{p["foreground"]}"',"",f'accent = "{p["accent"]}"',f'red     = "{p["red"]}"',""]+[f'color{i:<2} = "{v}"' for i,v in enumerate(p["colors"])]
    return "\n".join(lines)+"\n"
def ghostty(p): return "\n".join([f"background = {p['background']}",f"foreground = {p['foreground']}",f"cursor-color = {p['accent']}",f"selection-background = {p['accent']}",*[f"palette = {i}={v}" for i,v in enumerate(p['colors'])]])+"\n"
def kitty(p): return "\n".join([f"foreground {p['foreground']}",f"background {p['background']}",f"cursor {p['accent']}",f"selection_foreground {p['background']}",f"selection_background {p['accent']}",*[f"color{i} {v}" for i,v in enumerate(p['colors'])]])+"\n"
def alacritty(p):
    c=p['colors']; names=['black','red','green','yellow','blue','magenta','cyan','white']; return "[colors.primary]\nbackground = '"+p['background']+"'\nforeground = '"+p['foreground']+"'\n\n[colors.cursor]\ntext = '"+p['background']+"'\ncursor = '"+p['accent']+"'\n\n[colors.normal]\n"+"\n".join(f"{n} = '{v}'" for n,v in zip(names,c[:8]))+"\n\n[colors.bright]\n"+"\n".join(f"{n} = '{v}'" for n,v in zip(names,c[8:]))+"\n"
def wezterm(p):
    c=p['colors']; return "return {\n  foreground = '"+p['foreground']+"',\n  background = '"+p['background']+"',\n  cursor_bg = '"+p['accent']+"',\n  cursor_fg = '"+p['background']+"',\n  ansi = {"+", ".join(repr(v) for v in c[:8])+"},\n  brights = {"+", ".join(repr(v) for v in c[8:])+"},\n}\n"
def windows(p, mode):
    c=p['colors']; return json.dumps({"name":f"Neon Mary: Amélie (2001) {mode}","background":p['background'],"foreground":p['foreground'],"cursorColor":p['accent'],"black":c[0],"red":c[1],"green":c[2],"yellow":c[3],"blue":c[4],"purple":c[5],"cyan":c[6],"white":c[7],"brightBlack":c[8],"brightRed":c[9],"brightGreen":c[10],"brightYellow":c[11],"brightBlue":c[12],"brightPurple":c[13],"brightCyan":c[14],"brightWhite":c[15]},indent=2)+"\n"
def hermes(p, mode):
    c=p['colors']; dim=muted(c[8], p['background'], p['foreground']); return f'''name: neon-mary-amelie-{mode}
description: "Neon Mary: Amélie (2001) — Parisian café, warm ochre, poppy red, and teal ({mode})."
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
  welcome: A little bit of happiness.
  goodbye: Times are hard for dreamers.
  help_header: "◤ Neon Mary: Amélie — Commands"
spinner:
  waiting_faces: ["(◉)", "(◎)", "(⊙)"]
  thinking_faces: ["(⌁)", "(⊹)"]
  thinking_verbs: [noticing, wandering, imagining]
  wings: [["⟪◤", "◥⟫"], ["⟪△", "△⟫"]]
tool_prefix: ┊
'''
def wallpaper(source,out,w,h,mode):
    out.parent.mkdir(parents=True,exist_ok=True)
    is4k = (w==3840 and h==2160)
    base = source if is4k else ROOT/'wallpapers'/'amelie'/mode/'4k.png'
    # Grade only on the 4k pass; the other sizes are resized from the already
    # graded 4k, so re-applying would double-wash them.
    grade = ([] if not is4k else
             (['-modulate','94,74,100'] if mode=='dark'
              else light_grade_args(PALETTES['light']['background'])))
    cmd=['magick',str(base),'-resize',f'{w}x{h}^','-gravity','center','-extent',f'{w}x{h}',*grade,str(out)]; subprocess.run(cmd,check=True)
def main():
    if not SOURCE.exists(): raise SystemExit(f'Missing source: {SOURCE}')
    for mode,base in PALETTES.items():
        p=dict(base); p['mode']=mode; write(ROOT/'palettes'/f'amelie-{mode}.json',json.dumps(p,indent=2)+'\n'); write(ROOT/'hermes'/'skins'/f'neon-mary-amelie-{mode}.yaml',hermes(p,mode)); om=ROOT/'omarchy'/'themes'/f'neon-mary-amelie-{mode}'; (om/'backgrounds').mkdir(parents=True,exist_ok=True); write(om/'colors.toml',toml(p)); write(om/'icons.theme','Yaru-blue\n')
        for name,content in {'ghostty.conf':ghostty(p),'kitty.conf':kitty(p),'alacritty.toml':alacritty(p),'wezterm.lua':wezterm(p),'windows-terminal.json':windows(p, mode),'fzf.conf':f"--color=bg:{p['background']},fg:{p['foreground']},hl:{p['accent']},border:{p['accent']},prompt:{p['accent']},pointer:{p['red']}\n",'iterm2.json':json.dumps({'Name':f'Neon Mary: Amélie (2001) {mode}','Background Color':dict(zip(('Red Component','Green Component','Blue Component'),rgb(p['background']))),'Foreground Color':dict(zip(('Red Component','Green Component','Blue Component'),rgb(p['foreground'])))},indent=2)+'\n','Terminal.app.terminal':json.dumps({'name':f'Neon Mary: Amélie (2001) {mode}','profile':'Neon Mary: Amélie (2001)','colors':p['colors']},indent=2)+'\n'}.items(): write(ROOT/'terminals'/'amelie'/mode/name,content)
        write(ROOT/'editors'/'amelie'/mode/'vscode-color-theme.json',json.dumps({'name':f'Neon Mary: Amélie (2001) {mode}','type':mode,'colors':{'editor.background':p['background'],'editor.foreground':p['foreground'],'terminal.ansiCyan':p['colors'][6],'terminal.ansiMagenta':p['colors'][5],'terminal.ansiRed':p['red'],'terminal.ansiGreen':p['colors'][2]},'tokenColors':[]},indent=2)+'\n'); write(ROOT/'editors'/'amelie'/mode/'vim.vim',f'" Neon Mary: Amélie (2001) {mode} palette\nlet g:neon_mary_amelie_background = "{p["background"]}"\nlet g:neon_mary_amelie_foreground = "{p["foreground"]}"\n'); write(ROOT/'editors'/'amelie'/mode/'tmux.conf',f'set -g status-style "bg={p["background"]},fg={p["foreground"]}"\nset -g pane-active-border-style "fg={p["accent"]}"\nset -g message-style "bg={p["background"]},fg={p["accent"]}"\n')
        for name,(w,h) in RESOLUTIONS.items(): out=ROOT/'wallpapers'/'amelie'/mode/f'{name}.png'; wallpaper(SOURCE,out,w,h,mode); shutil.copy2(out,om/'backgrounds'/f'{name}.png')
    write(ROOT/'omarchy'/'amelie-README.md','# Neon Mary: Amélie (2001) Omarchy themes\n\nNeon Mary is the family; these are the Amélie variant native packages.\n')
if __name__=='__main__': main()
