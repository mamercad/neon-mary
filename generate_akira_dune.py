#!/usr/bin/env python3
"""Generate the Neon Mary: Akira (1988) and Dune (2021) variants."""
from pathlib import Path
import json, shutil, subprocess
from palette_utils import light_grade_args, muted, pick

ROOT = Path(__file__).resolve().parent
SOURCE = Path.home() / "Pictures" / "mary.png"
RESOLUTIONS = {"4k": (3840, 2160), "wqhd": (2560, 1440), "qhd": (1920, 1080), "16-10": (2560, 1600), "3-2": (2160, 1440), "4-3": (2048, 1536), "1-1": (2048, 2048), "9-16": (1440, 2560)}
VARIANTS = {
    "akira": {"title":"Akira (1988)", "tagline":"NEO-TOKYO IS ABOUT TO EXPLODE.", "caption":"vermilion / neo-tokyo", "welcome":"Neo-Tokyo is online.", "goodbye":"The city is still burning.", "dark":{"background":"#080d14","foreground":"#f5eee2","accent":"#ef3b24","red":"#ff5142","colors":["#080d14","#ff5142","#4dc4d8","#f3b72b","#2369a0","#b62d68","#16a9d1","#f5eee2","#182333","#ff806b","#83e3e8","#ffd96b","#55a2ce","#ed6b9a","#ff9a73","#fffaf0"]}, "light":{"background":"#eef3f1","foreground":"#191c23","accent":"#c52f28","red":"#a92328","colors":["#eef3f1","#a92328","#167480","#996600","#1e5480","#8d2351","#08759a","#191c23","#a8b6bb","#cf4c48","#3e969d","#b98413","#447da5","#ad5275","#c45a42","#191c23"]}},
    "dune": {"title":"Dune (2021)", "tagline":"FEAR IS THE MIND-KILLER.", "caption":"spice orange / deep desert", "welcome":"The desert remembers.", "goodbye":"Walk without rhythm.", "dark":{"background":"#10191a","foreground":"#f4ead3","accent":"#d88a3d","red":"#c95a3d","colors":["#10191a","#c95a3d","#8c9b62","#d88a3d","#3e7180","#8a6470","#b8a06a","#f4ead3","#253536","#e47a53","#b1bd7c","#f0b45e","#6c9eaa","#b18a99","#e0b06a","#fff8e6"]}, "light":{"background":"#f3ead8","foreground":"#27231d","accent":"#a65c25","red":"#9c3f2e","colors":["#f3ead8","#9c3f2e","#566b3e","#a65c25","#285a69","#754c55","#876839","#27231d","#b9ad99","#b95740","#758b55","#bd7c37","#4d8190","#996d73","#b47a3c","#27231d"]}},
}

def write(path, text): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding='utf-8')
def rgb(v): return tuple(int(v[i:i+2],16)/255 for i in (1,3,5))
def colors_toml(p):
    h=[f'mode = "{p["mode"]}"','',f'background = "{p["background"]}"',f'foreground = "{p["foreground"]}"','',f'accent = "{p["accent"]}"',f'red     = "{p["red"]}"','']
    return '\n'.join(h+[f'color{i:<2} = "{v}"' for i,v in enumerate(p['colors'])])+'\n'
def ghostty(p): return '\n'.join([f"background = {p['background']}",f"foreground = {p['foreground']}",f"cursor-color = {p['accent']}",f"selection-background = {p['accent']}",*[f"palette = {i}={v}" for i,v in enumerate(p['colors'])]])+'\n'
def kitty(p): return '\n'.join([f"foreground {p['foreground']}",f"background {p['background']}",f"cursor {p['accent']}",f"selection_foreground {p['background']}",f"selection_background {p['accent']}",*[f"color{i} {v}" for i,v in enumerate(p['colors'])]])+'\n'
def alacritty(p):
    c=p['colors']; n=['black','red','green','yellow','blue','magenta','cyan','white']
    return "[colors.primary]\nbackground = '"+p['background']+"'\nforeground = '"+p['foreground']+"'\n\n[colors.cursor]\ntext = '"+p['background']+"'\ncursor = '"+p['accent']+"'\n\n[colors.normal]\n"+'\n'.join(f"{x} = '{v}'" for x,v in zip(n,c[:8]))+"\n\n[colors.bright]\n"+'\n'.join(f"{x} = '{v}'" for x,v in zip(n,c[8:]))+'\n'
def wezterm(p):
    c=p['colors']; return "return {\n  foreground = '"+p['foreground']+"',\n  background = '"+p['background']+"',\n  cursor_bg = '"+p['accent']+"',\n  cursor_fg = '"+p['background']+"',\n  ansi = {"+', '.join(repr(v) for v in c[:8])+"},\n  brights = {"+', '.join(repr(v) for v in c[8:])+"},\n}\n"
def windows(p, title, mode):
    c=p['colors']; n=['black','red','green','yellow','blue','purple','cyan','white']; d={'name':f'Neon Mary: {title} {mode}','background':p['background'],'foreground':p['foreground'],'cursorColor':p['accent']}; d.update(dict(zip(n,c[:8]))); d.update(dict(zip(['bright'+x.title() for x in n],c[8:]))); return json.dumps(d,indent=2)+'\n'
def hermes(p, tag, title, mode, v):
    c=p['colors']; dim=muted(c[8],p['background'],p['foreground']); thinking=pick(p['background'],p['foreground'],c[5],c[13])
    return f'''name: neon-mary-{tag}-{mode}
description: "Neon Mary: {title} — {v['caption']} ({mode})."
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
  welcome: {v['welcome']}
  goodbye: {v['goodbye']}
  help_header: "◤ Neon Mary: {title} — Commands"
spinner:
  waiting_faces: ["(◉)", "(◎)", "(⊙)"]
  thinking_faces: ["(⌁)", "(⊹)"]
  thinking_verbs: ["mapping", "decoding", "observing"]
  wings: [["⟪◤", "◥⟫"], ["⟪△", "△⟫"]]
tool_prefix: ┊
'''
def wallpaper(out, tag, size, mode):
    out.parent.mkdir(parents=True,exist_ok=True); w,h=size; is4k=size==(3840,2160); base=SOURCE if is4k else ROOT/'wallpapers'/tag/mode/'4k.png'; grade=[] if not is4k else (["-modulate","86,80,100"] if mode=='dark' else light_grade_args('#f3ead8'))
    subprocess.run(['magick',str(base),'-resize',f'{w}x{h}^','-gravity','center','-extent',f'{w}x{h}',*grade,str(out)],check=True)
def main():
    if not SOURCE.exists(): raise SystemExit(f'Missing source: {SOURCE}')
    for tag,v in VARIANTS.items():
      for mode,base in v.items():
        if mode not in ('dark','light'): continue
        p=dict(base,mode=mode); slug=f'neon-mary-{tag}-{mode}'; om=ROOT/'omarchy'/'themes'/slug; (om/'backgrounds').mkdir(parents=True,exist_ok=True)
        write(ROOT/'palettes'/f'{tag}-{mode}.json',json.dumps(p,indent=2)+'\n'); write(ROOT/'hermes'/'skins'/f'{slug}.yaml',hermes(p,tag,v['title'],mode,v)); write(om/'colors.toml',colors_toml(p)); write(om/'icons.theme','Yaru-blue\n')
        ex={'ghostty.conf':ghostty(p),'kitty.conf':kitty(p),'alacritty.toml':alacritty(p),'wezterm.lua':wezterm(p),'windows-terminal.json':windows(p,v['title'],mode),'fzf.conf':f"--color=bg:{p['background']},fg:{p['foreground']},hl:{p['accent']},border:{p['accent']},prompt:{p['accent']},pointer:{p['red']}\n"}
        for name,text in ex.items(): write(ROOT/'terminals'/tag/mode/name,text)
        write(ROOT/'editors'/tag/mode/'vscode-color-theme.json',json.dumps({'name':f"Neon Mary: {v['title']} {mode}",'type':mode,'colors':{'editor.background':p['background'],'editor.foreground':p['foreground'],'terminal.ansiCyan':p['colors'][6],'terminal.ansiMagenta':p['colors'][5],'terminal.ansiRed':p['red'],'terminal.ansiGreen':p['colors'][2]},'tokenColors':[]},indent=2)+'\n')
        write(ROOT/'editors'/tag/mode/'vim.vim',f'" Neon Mary: {v["title"]} {mode} palette\nlet g:neon_mary_{tag}_background = "{p["background"]}"\nlet g:neon_mary_{tag}_foreground = "{p["foreground"]}"\n'); write(ROOT/'editors'/tag/mode/'tmux.conf',f'set -g status-style "bg={p["background"]},fg={p["foreground"]}"\nset -g pane-active-border-style "fg={p["accent"]}"\nset -g message-style "bg={p["background"]},fg={p["accent"]}"\n')
        for name,size in RESOLUTIONS.items():
          out=ROOT/'wallpapers'/tag/mode/f'{name}.png'; wallpaper(out,tag,size,mode); shutil.copy2(out,om/'backgrounds'/f'{name}.png')
      write(ROOT/'omarchy'/f'{tag}-README.md',f"# Neon Mary: {v['title']}\n\nNeon Mary is the theme family; these are the {v['title']} variant native Omarchy packages.\n")
if __name__=='__main__': main()
