#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import json
ROOT=Path(__file__).resolve().parent
expected={"4k":(3840,2160),"wqhd":(2560,1440),"qhd":(1920,1080),"16-10":(2560,1600),"3-2":(2160,1440),"4-3":(2048,1536),"1-1":(2048,2048),"9-16":(1440,2560)}
for tag in ('dark-city','fifth-element'):
 for mode in ('dark','light'):
  p=json.loads((ROOT/'palettes'/f'{tag}-{mode}.json').read_text()); assert p['mode']==mode
  for n,size in expected.items():
   for base in (ROOT/'wallpapers'/tag/mode,ROOT/'omarchy'/'themes'/f'neon-mary-{tag}-{mode}'/'backgrounds'):
    path=base/f'{n}.png'; assert path.exists(),path
    with Image.open(path) as im: assert im.size==size,(path,im.size,size)
  assert (ROOT/'hermes'/'skins'/f'neon-mary-{tag}-{mode}.yaml').exists()
print('validated: Dark City and The Fifth Element dark/light variants, 32 wallpapers, Omarchy packages, and Hermes skins')
