#!python3
#-*- coding: utf-8 -*-
from __future__ import print_function

from PIL import Image, ImageDraw, ImageFont

# get an image
cover = Image.open('Syberia.jpg').convert('RGBA')
#cover = Image.open('Seasons.jpg').convert('RGBA')

def draw_text(d, text, font, x, y):
    width = d.textsize(text, font=font)[0]
    d.text((x, y), text, font=font, fill=(255,165,12,255))    


txt = Image.new('RGBA', cover.size, (255,255,255,0))
## get a font
fnt = [ImageFont.truetype('Purisa.ttf', 240), ImageFont.truetype('Purisa.ttf', 60)]
## get a drawing context
d = ImageDraw.Draw(txt)

#Text = "#3"
Text = "#4"
#draw_text(d, "Skyrim", fnt[0], 400)
#draw_text(d, "25.10.2017 20:00", fnt[1], 550)
x = (cover.size[0] - d.textsize(Text, font=fnt[0])[0])-20
y = (cover.size[1] - d.textsize(Text, font=fnt[0])[1])/2+100
# print x, y, cover.size
draw_text(d, Text, fnt[0], x, y)

out = Image.alpha_composite(cover, txt)
background = Image.new('RGB', cover.size, (0,0,0))
background.paste(out, out.split()[-1])
background.save("Syberia1_4.jpg")
#background.save("Seasons_4.jpg")
#out.show()
