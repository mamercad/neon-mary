#!/usr/bin/env python3
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent
TEMPLATE=(ROOT/'screenshots/cinematic-template.svg').read_text()
variants={
'dark-city':{'title':'Dark City (1998)','tag':'dark-city','bg':'#08090d','shade':'#05060a','accent':'#7897bd','violet':'#6d6a8f','green':'#697b70','amber':'#b18b5c','red':'#a64b4b','fg':'#e7edf2','muted':'#7897bd','mood':'clockwork noir / steel blue / sodium amber','palette':'steel blue / violet / sodium amber','line':'THE CITY IS DREAMING.'},
'fifth-element':{'title':'The Fifth Element (1997)','tag':'fifth-element','bg':'#100b16','shade':'#08070d','accent':'#00cce8','violet':'#d04fc1','green':'#62d88a','amber':'#f5c842','red':'#ff643e','fg':'#fff0de','muted':'#75cde0','mood':'electric cyan / violet / solar amber','palette':'cyan / violet / solar amber','line':'MULTIPASS ACCEPTED.'},
'dark-city':{'title':'Dark City (1998)','tag':'dark-city','bg':'#08090d','shade':'#05060a','accent':'#7897bd','violet':'#6d6a8f','green':'#697b70','amber':'#b18b5c','red':'#a64b4b','fg':'#e7edf2','muted':'#7897bd','mood':'clockwork noir / steel blue / sodium amber','palette':'steel blue / violet / sodium amber','line':'THE CITY IS DREAMING.'},
'fifth-element':{'title':'The Fifth Element (1997)','tag':'fifth-element','bg':'#100b16','shade':'#08070d','accent':'#00cce8','violet':'#d04fc1','green':'#62d88a','amber':'#f5c842','red':'#ff643e','fg':'#fff0de','muted':'#75cde0','mood':'electric cyan / violet / solar amber','palette':'cyan / violet / solar amber','line':'MULTIPASS ACCEPTED.'},
}
for tag,v in variants.items():
 s=TEMPLATE
 for key,value in v.items(): s=s.replace('VAR_'+key.upper(),value)
 s=s.replace('VAR_PALETTE',v['palette'])
 (ROOT/f'screenshots/desktop-{tag}-dark-example.svg').write_text(s)
 subprocess.run(['magick',str(ROOT/f'screenshots/desktop-{tag}-dark-example.svg'),'-background',v['bg'],'-density','96',str(ROOT/f'screenshots/desktop-{tag}-dark-example.png')],check=True)
print('rendered:', ', '.join(f'desktop-{x}-dark-example.png' for x in variants))
