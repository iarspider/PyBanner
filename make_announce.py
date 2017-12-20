#!python3
#-*- coding: utf-8 -*-
from __future__ import print_function

import os

from PIL import Image, ImageDraw, ImageFont

if os.name != 'posix':
    root = r"c:\Windows\Fonts"
else:
    root = "/usr/share/fonts/truetype/tlwg/"

# purisa = os.path.join(root, 'Purisa.ttf')
purisa = os.path.join(root, 'segoepr.ttf')
print (purisa)

# get an image
#cover = Image.open('Skyrim.jpg').convert('RGBA')
cover = Image.open('Infra.jpg').convert('RGBA')
#cover = Image.open('syberia2.jpg').convert('RGBA')

banner = Image.open('Plzstandby.png').convert('RGBA')

def draw_text(d, text, font, y):
    global label_max_width
    width = d.textsize(text, font=font)[0]
    x = (label_max_width - width) / 2 + 562
    d.text((x, y), text, font=font, fill=(255,255,255,255))    


left_margin = 562
right_margin = cover.size[0] + 105
label_max_width = banner.size[0] - left_margin - right_margin

txt = Image.new('RGBA', banner.size, (255,255,255,0))
txt.paste(cover, ((banner.size[0] - cover.size[0])-95, round((banner.size[1] - cover.size[1])/2)))
## get a font
fnt = [ImageFont.truetype(purisa, 120), ImageFont.truetype(purisa, 60)]
## get a drawing context
d = ImageDraw.Draw(txt)

draw_text(d, "Infra", fnt[0], 350)
draw_text(d, u"По следам дядюшки Зи - 5", fnt[1], 550)
draw_text(d, u"19 декабря в 20:00", fnt[1], 650)

out = Image.alpha_composite(banner, txt)
#out.show()
background = Image.new('RGB', out.size, (0,0,0))
background.paste(out, out.split()[-1])
background.save("Infra_20171219.jpg") 

print("Done")
