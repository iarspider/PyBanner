#!python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import codecs
import configparser
import datetime
import os

from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help="Config file location (default: config.ini)", dest="config",
                    default="config.ini")
parser.add_argument('-d', '--date', help="Stream date, default today, format DD-MM", dest="date",
                    default=datetime.datetime.now().strftime("%d-%m"))
parser.add_argument('-t', '--time', help="Stream time, default 20:00", dest="time", default="20:00")
parser.add_argument("game", help="Game")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.config, "utf-8")

if os.name != 'posix':
    root = r"c:\Windows\Fonts"
else:
    root = "/usr/share/fonts/truetype/tlwg/"

# purisa = os.path.join(root, 'Purisa.ttf')
purisa = os.path.join(root, 'segoepr.ttf')
# print(purisa)

if not config.has_section(args.game):
    print("Game {0} not found in config file {1}".format(args.game, args.config))
    exit(0)

# get an image
# cover = Image.open('Skyrim.jpg').convert('RGBA')
# cover = Image.open('Infra.jpg').convert('RGBA')
cover = Image.open(config[args.game]['cover']).convert('RGBA')

banner = Image.open(config[args.game]['banner']).convert('RGBA')


def draw_text(d_, text, font, y):
    global label_max_width
    width = d.textsize(text, font=font)[0]
    x = (label_max_width - width) / 2 + 562
    d_.text((x, y), text, font=font, fill=(255, 255, 255, 255))


left_margin = 562
right_margin = cover.size[0] + 105
label_max_width = banner.size[0] - left_margin - right_margin

txt = Image.new('RGBA', banner.size, (255, 255, 255, 0))
txt.paste(cover, ((banner.size[0] - cover.size[0]) - 95, round((banner.size[1] - cover.size[1]) / 2)))
# get a font
fnt = [ImageFont.truetype(purisa, 120), ImageFont.truetype(purisa, 60)]
# get a drawing context
d = ImageDraw.Draw(txt)

draw_text(d, config[args.game]['line1'].format(**config[args.game]), fnt[0], 350)
draw_text(d, config[args.game]['line2'].format(**config[args.game]), fnt[1], 550)

game_count = int(config[args.game].get('count', '1'))
config[args.game]['count'] = str(game_count + 1)

with codecs.open(args.config, 'w', 'utf-8') as f:
    config.write(f)

stream_date = datetime.datetime.strptime(args.date, "%d-%m")

month_name = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября",
              "декабря"][stream_date.month - 1]

draw_text(d, u"{0} {1} в {2}".format(stream_date.day, month_name, args.time), fnt[1], 650)

out = Image.alpha_composite(banner, txt)
# out.show()
background = Image.new('RGB', out.size, (0, 0, 0))
background.paste(out, out.split()[-1])
background.save("{0}_{1}_{2}{3}.jpg".format(args.game.replace(' ', '_'), game_count, stream_date.month, stream_date.day))

print("Done")
