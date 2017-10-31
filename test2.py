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
fnt = [ImageFont.truetype('/usr/share/fonts/truetype/tlwg/Purisa.ttf', 120), ImageFont.truetype('/usr/share/fonts/truetype/tlwg/Purisa.ttf', 60)]
## get a drawing context
d = ImageDraw.Draw(txt)

#draw_text(d, "Skyrim", fnt[0], 400)
#draw_text(d, "25.10.2017 20:00", fnt[1], 550)
x = (cover.size[0] - d.textsize("#1", font=fnt[1])[0])/2+20
y = cover.size[1] - d.textsize("#1", font=fnt[1])[1]
print x, y, cover.size
draw_text(d, "#1", fnt[1], x, y)

out = Image.alpha_composite(cover, txt)

out.save("Syberia1.jpg")
#out.show()

exit(0)
