#-*- coding: utf-8 -*-
from sys import argv
from PIL import Image, ImageDraw, ImageFont
# get an image
cover = Image.open('Syberia.jpg').convert('RGBA')

def draw_text(d, text, font, x, y):
    width = d.textsize(text, font=font)[0]
    d.text((x, y), text, font=font, fill=(0,0,0,255))    


txt = Image.new('RGBA', cover.size, (255,255,255,0))
## get a font
fnt = [ImageFont.truetype('Purisa.ttf', 120), ImageFont.truetype('Purisa.ttf', 60)]
## get a drawing context
d = ImageDraw.Draw(txt)

Text = "#2"
#draw_text(d, "Skyrim", fnt[0], 400)
#draw_text(d, "25.10.2017 20:00", fnt[1], 550)
x = (cover.size[0] - d.textsize(Text, font=fnt[1])[0])/2+20
y = cover.size[1] - d.textsize(Text, font=fnt[1])[1]
# print x, y, cover.size
draw_text(d, Text, fnt[1], x, y)

out = Image.alpha_composite(cover, txt)
background = Image.new('RGB', cover.size, (0,0,0))
background.paste(out, out.split()[-1])
background.save("Syberia1_2.jpg")
#out.show()

exit(0)
