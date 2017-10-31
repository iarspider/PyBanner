#-*- coding: utf-8 -*-
from sys import argv
from PIL import Image, ImageDraw, ImageFont
# get an image
cover = Image.open('Skyrim.jpg').convert('RGBA')
banner = Image.open('Plzstandby.png').convert('RGBA')

def draw_text(d, text, font, y):
    global label_max_width
    print label_max_width
    width = d.textsize(text, font=font)[0]
    x = (label_max_width - width) / 2 + 562
    d.text((x, y), text, font=font, fill=(255,255,255,255))    


left_margin = 562
right_margin = cover.size[0] + 105
label_max_width = banner.size[0] - left_margin - right_margin
print label_max_width

txt = Image.new('RGBA', banner.size, (255,255,255,0))
txt.paste(cover, ((banner.size[0] - cover.size[0])-105, (banner.size[1] - cover.size[1])/2))
## get a font
fnt = [ImageFont.truetype('/usr/share/fonts/truetype/tlwg/Purisa.ttf', 120), ImageFont.truetype('/usr/share/fonts/truetype/tlwg/Purisa.ttf', 60)]
## get a drawing context
d = ImageDraw.Draw(txt)

draw_text(d, "Skyrim", fnt[0], 400)
draw_text(d, "25.10.2017 20:00", fnt[1], 550)

out = Image.alpha_composite(banner, txt)

#out.save("Skyrim_20171025.jpg")
out.show()

exit(0)
