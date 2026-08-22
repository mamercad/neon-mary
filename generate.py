#!/usr/bin/env python3
"""Generate Neon Mary wallpaper variants and portable theme resources."""
from pathlib import Path
import json, shutil, subprocess

ROOT = Path(__file__).resolve().parent
SRC = Path.home() / "Wallpapers" / "blade-runner-neon-mary-4k.png"
ORIGINAL = Path.home() / "Pictures" / "mary.png"
RESOLUTIONS = {"4k": (3840, 2160), "wqhd": (2560, 1440), "qhd": (1920, 1080), "16-10": (2560, 1600), "3-2": (2160, 1440), "4-3": (2048, 1536), "1-1": (2048, 2048), "9-16": (1440, 2560)}
PALETTES = {
    "dark": {"background":"#0a0c12", "foreground":"#eafcff", "accent":"#00e5ff", "red":"#ff4d6d", "colors":["#0a0c12","#ff4d6d","#3dffb0","#ffe066","#4d8bff","#ff2adb","#00e5ff","#c9d6e3","#4a5568","#ff7a90","#7dffd0","#fff0a0","#7fb0ff","#ff6fe0","#7ff2ff","#ffffff"]},
    "light": {"background":"#f3f7f8", "foreground":"#101822", "accent":"#007f99", "red":"#b32645", "colors":["#f3f7f8","#b32645","#087a55","#8a6200","#2458a8","#a3178d","#007f99","#293743","#71818c","#8f1d3b","#087a55","#725d00","#2458a8","#86106f","#006a7d","#101822"]},
}

def run(*args):
    subprocess.run(args, check=True)

def toml(p):
    c=p["colors"]
    lines=[f'mode = "{p["mode"]}"', "", f'background = "{p["background"]}"', f'foreground = "{p["foreground"]}"', "", f'accent = "{p["accent"]}"', f'red     = "{p["red"]}"', ""]
    lines += [f'color{i:<2} = "{v}"' for i,v in enumerate(c)]
    return "\n".join(lines)+"\n"

def ghostty(p):
    return "\n".join([f"background = {p['background']}", f"foreground = {p['foreground']}", f"cursor-color = {p['accent']}", "selection-foreground = #ffffff", f"selection-background = {p['accent']}", *[f"palette = {i}={v}" for i,v in enumerate(p['colors'])]])+"\n"

def kitty(p):
    names=['black','red','green','yellow','blue','magenta','cyan','white','bright_black','bright_red','bright_green','bright_yellow','bright_blue','bright_magenta','bright_cyan','bright_white']
    return "\n".join([f"foreground {p['foreground']}",f"background {p['background']}",f"cursor {p['accent']}",f"selection_foreground {p['background']}",f"selection_background {p['accent']}",*[(f"color{i} {v}") for i,v in enumerate(p['colors'])]])+"\n"

def wezterm(p):
    c=p['colors']; return "return {\n  foreground = '"+p['foreground']+"',\n  background = '"+p['background']+"',\n  cursor_bg = '"+p['accent']+"',\n  cursor_fg = '"+p['background']+"',\n  ansi = {"+", ".join(repr(x) for x in c[:8])+"},\n  brights = {"+", ".join(repr(x) for x in c[8:])+"},\n}\n"

def alacritty(p):
    c=p['colors']; return "[colors.primary]\nbackground = '"+p['background']+"'\nforeground = '"+p['foreground']+"'\n\n[colors.cursor]\ntext = '"+p['background']+"'\ncursor = '"+p['accent']+"'\n\n[colors.normal]\n"+"\n".join(f"{n} = '{v}'" for n,v in zip(['black','red','green','yellow','blue','magenta','cyan','white'],c[:8]))+"\n\n[colors.bright]\n"+"\n".join(f"{n} = '{v}'" for n,v in zip(['black','red','green','yellow','blue','magenta','cyan','white'],c[8:]))+"\n"

def windows(p):
    c=p['colors']; return json.dumps({"name":"Neon Mary","background":p['background'],"foreground":p['foreground'],"cursorColor":p['accent'],"black":c[0],"red":c[1],"green":c[2],"yellow":c[3],"blue":c[4],"purple":c[5],"cyan":c[6],"white":c[7],"brightBlack":c[8],"brightRed":c[9],"brightGreen":c[10],"brightYellow":c[11],"brightBlue":c[12],"brightPurple":c[13],"brightCyan":c[14],"brightWhite":c[15]}, indent=2)+"\n"

def fzf(p):
    return f"--color=bg:{p['background']},fg:{p['foreground']},hl:{p['accent']},fg+: {p['foreground']},bg+: {p['background']},hl+: {p['accent']},border:{p['accent']},prompt:{p['accent']},pointer:{p['red']},info:{p['accent']}\n"

def hermes(p, mode):
    accent=p['accent']; bg=p['background']; fg=p['foreground']; return f'''name: neon-mary-{mode}\ndescription: Neon Mary — Blade Runner cyan, magenta, and rain-black ({mode}).\ncolors:\n  background: '{bg}'\n  status_bar_bg: '{bg}'\n  ui_accent: '{accent}'\n  banner_accent: '{accent}'\n  prompt: '{accent}'\n  input_rule: '{p['red']}'\n  banner_title: '{p['colors'][14]}'\n  ui_primary: '{p['colors'][14]}'\n  session_label: '{p['colors'][14]}'\n  response_border: '{p['colors'][6]}'\n  banner_text: '{fg}'\n  ui_text: '{fg}'\n  ui_label: '{p['colors'][7]}'\n  banner_dim: '{p['colors'][8]}'\n  banner_border: '{p['colors'][6]}'\n  ui_border: '{p['colors'][6]}'\n  session_border: '{p['colors'][6]}'\n  ui_tool: '{p['colors'][2]}'\n  ui_thinking: '{p['colors'][5]}'\n  ui_ok: '{p['colors'][2]}'\n  ui_warn: '{p['colors'][3]}'\n  ui_error: '{p['red']}'\n  status_bar_text: '{p['colors'][7]}'\n  status_bar_good: '{p['colors'][2]}'\n  status_bar_warn: '{p['colors'][3]}'\n  status_bar_bad: '{p['colors'][9]}'\n  status_bar_critical: '{p['red']}'\n  syntax_string: '{p['colors'][2]}'\n  syntax_number: '{p['colors'][3]}'\n  syntax_keyword: '{p['colors'][14]}'\n  syntax_comment: '{p['colors'][8]}'\n  completion_menu_bg: '{bg}'\n  completion_menu_current_bg: '{p['colors'][6]}'\n  completion_menu_meta_bg: '{bg}'\nbranding:\n  agent_name: Hermes Agent\n  prompt_symbol: ❯\n  welcome: Wake up. Time to die.\n  goodbye: All those moments will be lost in time, like tears in rain.\n  help_header: ◤ Neon Mary — Commands\nspinner:\n  waiting_faces: ["(◉)", "(◎)", "(⊙)"]\n  thinking_faces: ["(⌁)", "(⊹)"]\n  thinking_verbs: [enhancing, dreaming, tracking]\n  wings: [["⟪◤", "◥⟫"], ["⟪△", "△⟫"]]\ntool_prefix: ┊\n'''

def main():
    if not SRC.exists() or not ORIGINAL.exists(): raise SystemExit(f"Missing source: {SRC if not SRC.exists() else ORIGINAL}")
    for mode, base in PALETTES.items():
        p=dict(base); p['mode']=mode
        (ROOT/'palettes').mkdir(exist_ok=True)
        (ROOT/'palettes'/f'{mode}.json').write_text(json.dumps(p, indent=2)+"\n")
        (ROOT/'hermes'/'skins').mkdir(parents=True, exist_ok=True)
        (ROOT/'hermes'/'skins'/f'neon-mary-{mode}.yaml').write_text(hermes(p,mode))
        (ROOT/'omarchy'/'themes'/f'neon-mary-{mode}'/'backgrounds').mkdir(parents=True, exist_ok=True)
        (ROOT/'omarchy'/'themes'/f'neon-mary-{mode}'/'colors.toml').write_text(toml(p))
        (ROOT/'omarchy'/'themes'/f'neon-mary-{mode}'/'icons.theme').write_text('Yaru-blue\n')
        (ROOT/'terminals'/mode).mkdir(parents=True, exist_ok=True)
        (ROOT/'terminals'/mode/'ghostty.conf').write_text(ghostty(p))
        (ROOT/'terminals'/mode/'kitty.conf').write_text(kitty(p))
        (ROOT/'terminals'/mode/'wezterm.lua').write_text(wezterm(p))
        (ROOT/'terminals'/mode/'alacritty.toml').write_text(alacritty(p))
        (ROOT/'terminals'/mode/'windows-terminal.json').write_text(windows(p))
        (ROOT/'terminals'/mode/'fzf.conf').write_text(fzf(p))
        (ROOT/'terminals'/mode/'iterm2.json').write_text(json.dumps({"Name":f"Neon Mary {mode}","Background Color":{"Red Component":int(p['background'][1:3],16)/255,"Green Component":int(p['background'][3:5],16)/255,"Blue Component":int(p['background'][5:7],16)/255},"Foreground Color":{"Red Component":int(p['foreground'][1:3],16)/255,"Green Component":int(p['foreground'][3:5],16)/255,"Blue Component":int(p['foreground'][5:7],16)/255}},indent=2)+"\n")
        (ROOT/'terminals'/mode/'Terminal.app.terminal').write_text(json.dumps({"name":f"Neon Mary {mode}","profile":"Neon Mary","colors":p['colors']},indent=2)+"\n")
        (ROOT/'editors'/mode).mkdir(parents=True, exist_ok=True)
        (ROOT/'editors'/mode/'vscode-color-theme.json').write_text(json.dumps({"name":f"Neon Mary {mode}","type":mode,"colors":{"editor.background":p['background'],"editor.foreground":p['foreground'],"terminal.ansiCyan":p['colors'][6],"terminal.ansiMagenta":p['colors'][5],"terminal.ansiRed":p['red'],"terminal.ansiGreen":p['colors'][2]},"tokenColors":[]},indent=2)+"\n")
        (ROOT/'editors'/mode/'vim.vim').write_text(f'" Neon Mary {mode} palette\n" Source the terminal palette or use a colorscheme adapter.\nlet g:neon_mary_background = "{p["background"]}"\nlet g:neon_mary_foreground = "{p["foreground"]}"\n')
        (ROOT/'editors'/mode/'tmux.conf').write_text(f'set -g status-style "bg={p["background"]},fg={p["foreground"]}"\nset -g pane-active-border-style "fg={p["accent"]}"\nset -g message-style "bg={p["background"]},fg={p["accent"]}"\n')
        for name,(w,h) in RESOLUTIONS.items():
            out=ROOT/'wallpapers'/mode/f'{name}.png'; out.parent.mkdir(parents=True,exist_ok=True)
            if name=='4k' and mode=='dark': shutil.copy2(SRC,out)
            elif name=='4k' and mode=='light': run('convert',str(SRC),'-brightness-contrast','12x4','-modulate','112,82,100',str(out))
            else:
                source=ROOT/'wallpapers'/mode/'4k.png'; run('convert',str(source),'-resize',f'{w}x{h}^','-gravity','center','-extent',f'{w}x{h}',str(out))
            shutil.copy2(out, ROOT/'omarchy'/'themes'/f'neon-mary-{mode}'/'backgrounds'/f'{name}.png')
    shutil.copy2(ORIGINAL, ROOT/'wallpapers'/'original-mary-1254.png')
    (ROOT/'omarchy'/'README.md').write_text('# Omarchy themes\n\nEach `neon-mary-{dark,light}` directory is a native theme package with `colors.toml`, `icons.theme`, and all generated background variants. Copy one into `~/.config/omarchy/themes/` and apply with `omarchy-theme-set neon-mary-dark`.\n\n`omarchy/generated/` contains portable downstream resource snapshots for the supported terminal/editor targets.\n')
if __name__ == '__main__': main()
