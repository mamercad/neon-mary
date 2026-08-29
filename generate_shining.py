#!/usr/bin/env python3
"""Generate the Neon Mary: The Shining (1980) variant."""
from pathlib import Path
import json, shutil, subprocess
from palette_utils import light_grade_args, muted, pick
from generate_akira_dune import RESOLUTIONS, write, rgb, colors_toml, ghostty, kitty, alacritty, wezterm, windows

ROOT=Path(__file__).resolve().parent; SOURCE=Path.home()/"Pictures"/"mary.png"
PALETTES={
'dark':{'background':'#100d0d','foreground':'#f3eee0','accent':'#c93532','red':'#e4473f','colors':['#100d0d','#e4473f','#5f8692','#d0a83c','#41677a','#8f3f45','#b65b42','#f3eee0','#332322','#f47763','#92b6bc','#ecd06b','#6e9aaa','#c2767a','#e4b36a','#fff9e8']},
'light':{'background':'#f3eee3','foreground':'#241c1b','accent':'#a52e2f','red':'#972c2d','colors':['#f3eee3','#972c2d','#3e6974','#8a620e','#31536a','#713c42','#8e4a39','#241c1b','#b8aaa0','#bd4b4d','#668994','#af861d','#52788a','#985f65','#b27a3d','#241c1b']}}

def hermes(p,mode):
 c=p['colors']; dim=muted(c[8],p['background'],p['foreground']); thinking=pick(p['background'],p['foreground'],c[5],c[13])
 return f'''name: neon-mary-shining-{mode}
description: "Neon Mary: The Shining (1980) — Overlook red, icy blue, mustard gold, and winter shadow ({mode})."
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
  welcome: All work and no play.
  goodbye: The hotel is closed.
  help_header: "◤ Neon Mary: The Shining — Commands"
spinner:
  waiting_faces: ["(◉)", "(◎)", "(⊙)"]
  thinking_faces: ["(⌁)", "(⊹)"]
  thinking_verbs: ["wandering", "listening", "observing"]
  wings: [["⟪◤", "◥⟫"], ["⟪△", "△⟫"]]
tool_prefix: ┊
'''
def wall(out,tag,size,mode):
 w,h=size; is4k=size==(3840,2160); base=SOURCE if is4k else ROOT/'wallpapers'/tag/mode/'4k.png'; grade=[] if not is4k else (["-modulate","84,78,100"] if mode=='dark' else light_grade_args(PALETTES['light']['background']))
 out.parent.mkdir(parents=True,exist_ok=True); subprocess.run(['magick',str(base),'-resize',f'{w}x{h}^','-gravity','center','-extent',f'{w}x{h}',*grade,str(out)],check=True)
def main():
 if not SOURCE.exists(): raise SystemExit(f'Missing source: {SOURCE}')
 for mode,base in PALETTES.items():
  p=dict(base,mode=mode); slug=f'neon-mary-shining-{mode}'; om=ROOT/'omarchy'/'themes'/slug; (om/'backgrounds').mkdir(parents=True,exist_ok=True)
  write(ROOT/'palettes'/f'shining-{mode}.json',json.dumps(p,indent=2)+'\n'); write(ROOT/'hermes'/'skins'/f'{slug}.yaml',hermes(p,mode)); write(om/'colors.toml',colors_toml(p)); write(om/'icons.theme','Yaru-blue\n')
  ex={'ghostty.conf':ghostty(p),'kitty.conf':kitty(p),'alacritty.toml':alacritty(p),'wezterm.lua':wezterm(p),'windows-terminal.json':windows(p,'The Shining (1980)',mode),'fzf.conf':f"--color=bg:{p['background']},fg:{p['foreground']},hl:{p['accent']},border:{p['accent']},prompt:{p['accent']},pointer:{p['red']}\n"}
  for n,t in ex.items(): write(ROOT/'terminals'/'shining'/mode/n,t)
  write(ROOT/'editors'/'shining'/mode/'vscode-color-theme.json',json.dumps({'name':f'The Shining (1980) {mode}','type':mode,'colors':{'editor.background':p['background'],'editor.foreground':p['foreground'],'terminal.ansiCyan':p['colors'][6],'terminal.ansiMagenta':p['colors'][5],'terminal.ansiRed':p['red'],'terminal.ansiGreen':p['colors'][2]},'tokenColors':[]},indent=2)+'\n')
  write(ROOT/'editors'/'shining'/mode/'vim.vim',f'" Neon Mary: The Shining (1980) {mode} palette\nlet g:neon_mary_shining_background = "{p["background"]}"\nlet g:neon_mary_shining_foreground = "{p["foreground"]}"\n'); write(ROOT/'editors'/'shining'/mode/'tmux.conf',f'set -g status-style "bg={p["background"]},fg={p["foreground"]}"\nset -g pane-active-border-style "fg={p["accent"]}"\nset -g message-style "bg={p["background"]},fg={p["accent"]}"\n')
  for n,s in RESOLUTIONS.items():
   out=ROOT/'wallpapers'/'shining'/mode/f'{n}.png'; wall(out,'shining',s,mode); shutil.copy2(out,om/'backgrounds'/f'{n}.png')
 write(ROOT/'omarchy'/'shining-README.md','# Neon Mary: The Shining (1980)\n\nNeon Mary is the theme family; these are The Shining variant native Omarchy packages.\n')
if __name__=='__main__': main()
