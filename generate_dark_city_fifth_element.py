#!/usr/bin/env python3
"""Generate the Neon Mary: Dark City (1998) and The Fifth Element (1997) variants."""
from pathlib import Path
import json, shutil, subprocess
ROOT=Path(__file__).resolve().parent
SOURCE=Path.home()/"Pictures"/"mary.png"
RES={"4k":(3840,2160),"wqhd":(2560,1440),"qhd":(1920,1080),"16-10":(2560,1600),"3-2":(2160,1440),"4-3":(2048,1536),"1-1":(2048,2048),"9-16":(1440,2560)}
VARIANTS={
 "dark-city": {"title":"Dark City (1998)","tag":"dark-city","dark":{"bg":"#08090d","fg":"#e7edf2","accent":"#7897bd","red":"#a64b4b","c":["#08090d","#a64b4b","#697b70","#b18b5c","#3d526b","#6d6a8f","#7897bd","#d0d8de","#262a32","#d36969","#8ca595","#d6af78","#607c9c","#9a95c2","#9fb8d0","#f4f7f8"]},"light":{"bg":"#e8edf0","fg":"#1b222a","accent":"#466581","red":"#8c3035","c":["#e8edf0","#8c3035","#3e5f4b","#80602d","#324c6a","#5b4e77","#466581","#1b222a","#a6b3ba","#a94347","#5d805f","#a17e42","#587696","#786a99","#52738d","#1b222a"]}},
 "fifth-element": {"title":"The Fifth Element (1997)","tag":"fifth-element","dark":{"bg":"#100b16","fg":"#fff0de","accent":"#00cce8","red":"#ff643e","c":["#100b16","#ff643e","#62d88a","#f5c842","#2874b8","#d04fc1","#00cce8","#fff0de","#38253e","#ff9478","#98f0ae","#ffe27b","#62a5e8","#ee86df","#75f3ff","#fff8ed"]},"light":{"bg":"#fff0df","fg":"#291722","accent":"#007e9a","red":"#c23b2d","c":["#fff0df","#c23b2d","#3c7c4d","#9b7010","#245d91","#9b397f","#007e9a","#291722","#c9a994","#dc5c47","#65a873","#b38d24","#4d83b8","#b85d9f","#238b9f","#291722"]}},
}
def write(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s)
def rgb(value): return tuple(int(value[i:i+2],16)/255 for i in (1,3,5))
def toml(p): return "\n".join([f'mode = "{p["mode"]}"',"",f'background = "{p["bg"]}"',f'foreground = "{p["fg"]}"',"",f'accent = "{p["accent"]}"',f'red     = "{p["red"]}"',""]+[f'color{i:<2} = "{v}"' for i,v in enumerate(p["c"])])+"\n"
def ghostty(p): return "\n".join([f"background = {p['bg']}",f"foreground = {p['fg']}",f"cursor-color = {p['accent']}",f"selection-background = {p['accent']}",*[f"palette = {i}={v}" for i,v in enumerate(p['c'])]])+"\n"
def kitty(p): return "\n".join([f"foreground {p['fg']}",f"background {p['bg']}",f"cursor {p['accent']}",f"selection_foreground {p['bg']}",f"selection_background {p['accent']}",*[f"color{i} {v}" for i,v in enumerate(p['c'])]])+"\n"
def alacritty(p):
 n=['black','red','green','yellow','blue','magenta','cyan','white']; c=p['c']; return "[colors.primary]\nbackground = '"+p['bg']+"'\nforeground = '"+p['fg']+"'\n\n[colors.cursor]\ntext = '"+p['bg']+"'\ncursor = '"+p['accent']+"'\n\n[colors.normal]\n"+"\n".join(f"{x} = '{y}'" for x,y in zip(n,c[:8]))+"\n\n[colors.bright]\n"+"\n".join(f"{x} = '{y}'" for x,y in zip(n,c[8:]))+"\n"
def wezterm(p): return "return {\n  foreground = '"+p['fg']+"',\n  background = '"+p['bg']+"',\n  cursor_bg = '"+p['accent']+"',\n  cursor_fg = '"+p['bg']+"',\n  ansi = {"+", ".join(repr(v) for v in p['c'][:8])+"},\n  brights = {"+", ".join(repr(v) for v in p['c'][8:])+"},\n}\n"
def windows(p,title):
 n=['black','red','green','yellow','blue','purple','cyan','white']; d={"name":f"Neon Mary: {title}","background":p['bg'],"foreground":p['fg'],"cursorColor":p['accent']}; d.update(dict(zip(n,p['c'][:8]))); d.update(dict(zip(['bright'+x.title() for x in n],p['c'][8:]))); return json.dumps(d,indent=2)+"\n"
def hermes(p,mode,title,tag):
 c=p['c']; return f'''name: neon-mary-{tag}-{mode}\ndescription: "Neon Mary: {title} — cinematic palette ({mode})."\ncolors:\n  background: '{p['bg']}'\n  status_bar_bg: '{p['bg']}'\n  ui_accent: '{p['accent']}'\n  banner_accent: '{p['accent']}'\n  prompt: '{p['accent']}'\n  input_rule: '{p['red']}'\n  banner_title: '{c[14]}'\n  ui_primary: '{c[14]}'\n  session_label: '{c[14]}'\n  response_border: '{c[6]}'\n  banner_text: '{p['fg']}'\n  ui_text: '{p['fg']}'\n  ui_label: '{c[7]}'\n  banner_dim: '{c[8]}'\n  banner_border: '{c[6]}'\n  ui_border: '{c[6]}'\n  session_border: '{c[6]}'\n  ui_tool: '{c[2]}'\n  ui_thinking: '{c[5]}'\n  ui_ok: '{c[2]}'\n  ui_warn: '{c[3]}'\n  ui_error: '{p['red']}'\n  status_bar_text: '{c[7]}'\n  status_bar_good: '{c[2]}'\n  status_bar_warn: '{c[3]}'\n  status_bar_bad: '{c[9]}'\n  status_bar_critical: '{p['red']}'\n  syntax_string: '{c[2]}'\n  syntax_number: '{c[3]}'\n  syntax_keyword: '{c[14]}'\n  syntax_comment: '{c[8]}'\n  completion_menu_bg: '{p['bg']}'\n  completion_menu_current_bg: '{c[6]}'\n  completion_menu_meta_bg: '{p['bg']}'\nbranding:\n  agent_name: Hermes Agent\n  prompt_symbol: ❯\n  welcome: {('The city is dreaming.' if tag=='dark-city' else 'Leeloo multipass.')}\n  goodbye: {('They built the city to see what makes us tick.' if tag=='dark-city' else 'Time not important. Only life important.')}\n  help_header: "◤ Neon Mary: {title} — Commands"\nspinner:\n  waiting_faces: ["(◉)", "(◎)", "(⊙)"]\n  thinking_faces: ["(⌁)", "(⊹)"]\n  thinking_verbs: [observing, tuning, traversing]\n  wings: [["⟪◤", "◥⟫"], ["⟪△", "△⟫"]]\ntool_prefix: ┊\n'''
def wallpaper(out,w,h,mode,source):
 tag = out.parts[-3]
 base = source if (w,h)==(3840,2160) else ROOT/'wallpapers'/tag/mode/'4k.png'
 grade=['-modulate','90,72,100'] if mode=='dark' else ['-modulate','106,52,100']
 out.parent.mkdir(parents=True, exist_ok=True)
 subprocess.run(['magick',str(base),'-resize',f'{w}x{h}^','-gravity','center','-extent',f'{w}x{h}',*grade,str(out)],check=True)
def main():
 if not SOURCE.exists(): raise SystemExit(f'Missing source: {SOURCE}')
 for tag,v in VARIANTS.items():
  for mode,base in v.items():
   if mode not in ('dark','light'): continue
   p=dict(base); p.update(mode=mode,accent=base['accent'],red=base['red']); write(ROOT/'palettes'/f'{tag}-{mode}.json',json.dumps(p,indent=2)+'\n'); write(ROOT/'hermes'/'skins'/f'neon-mary-{tag}-{mode}.yaml',hermes(p,mode,v['title'],tag)); om=ROOT/'omarchy'/'themes'/f'neon-mary-{tag}-{mode}'; (om/'backgrounds').mkdir(parents=True,exist_ok=True); write(om/'colors.toml',toml(p)); write(om/'icons.theme','Yaru-blue\n');
   for n,s in {'ghostty.conf':ghostty(p),'kitty.conf':kitty(p),'alacritty.toml':alacritty(p),'wezterm.lua':wezterm(p),'windows-terminal.json':windows(p,v['title']),'fzf.conf':f"--color=bg:{p['bg']},fg:{p['fg']},hl:{p['accent']},border:{p['accent']},prompt:{p['accent']},pointer:{p['red']}\n",'iterm2.json':json.dumps({'Name':f'Neon Mary: {v["title"]} {mode}','Background Color':dict(zip(('Red Component','Green Component','Blue Component'),rgb(p['bg']))),'Foreground Color':dict(zip(('Red Component','Green Component','Blue Component'),rgb(p['fg'])))},indent=2)+'\n','Terminal.app.terminal':json.dumps({'name':f'Neon Mary: {v["title"]} {mode}','profile':f'Neon Mary: {v["title"]}','colors':p['c']},indent=2)+'\n'}.items(): write(ROOT/'terminals'/tag/mode/n,s)
   write(ROOT/'editors'/tag/mode/'vscode-color-theme.json',json.dumps({'name':f'Neon Mary: {v["title"]} {mode}','type':mode,'colors':{'editor.background':p['bg'],'editor.foreground':p['fg'],'terminal.ansiCyan':p['c'][6],'terminal.ansiMagenta':p['c'][5],'terminal.ansiRed':p['red'],'terminal.ansiGreen':p['c'][2]},'tokenColors':[]},indent=2)+'\n'); write(ROOT/'editors'/tag/mode/'vim.vim',f'" Neon Mary: {v["title"]} {mode} palette\nlet g:neon_mary_{tag.replace("-", "_")}_background = "{p["bg"]}"\n'); write(ROOT/'editors'/tag/mode/'tmux.conf',f'set -g status-style "bg={p["bg"]},fg={p["fg"]}"\nset -g pane-active-border-style "fg={p["accent"]}"\n')
   for n,(w,h) in RES.items(): out=ROOT/'wallpapers'/tag/mode/f'{n}.png'; wallpaper(out,w,h,mode,SOURCE); shutil.copy2(out,om/'backgrounds'/f'{n}.png')
  write(ROOT/'omarchy'/f'{tag}-README.md',f'# Neon Mary: {v["title"]}\n\nNeon Mary is the theme family; these are the {v["title"]} variant native Omarchy packages.\n')
if __name__=='__main__': main()
