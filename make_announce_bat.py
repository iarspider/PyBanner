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
bg_image = Image.open(config[args.game]['background']).convert('RGBA')
game_image = Image.open(config[args.game]['game']).convert('RGBA')


def draw_text(d_, text, font, y):
    global label_max_width
    width, height = d.textsize(text, font=font)
    x = (label_max_width - width) / 2 + 562
    d_.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    return height


left_margin = 562
right_margin = bg_image.size[0] + 105
label_max_width = game_image.size[0] - left_margin - right_margin

canvas = Image.new('RGBA', bg_image.size, (255, 255, 255, 0))
canvas.paste(game_image,
             ((bg_image.size[0] - game_image.size[0]) - 95, round((bg_image.size[1] - game_image.size[1]) / 2)))
# get a font
fnt = [ImageFont.truetype(purisa, int(config[args.game].get('font', 60)) * 2),
       ImageFont.truetype(purisa, config[args.game].get('font1', 60))]
# get a drawing context
d = ImageDraw.Draw(canvas)

line_cnt = config[args.game].get('linec', 2)
y = int(config[args.game].get('start_y', 350))
for i in range(1, int(line_cnt) + 1):
    h = draw_text(d, config[args.game]['line{0}'.format(i)].format(**config[args.game]), fnt[0], y)
    y += h + int(config[args.game].get('pad_y', 10))

game_count = int(config[args.game].get('count', '1'))
config[args.game]['count'] = str(game_count + 1)

with codecs.open(args.config, 'w', 'utf-8') as f:
    config.write(f)

stream_date = datetime.datetime.strptime(args.date, "%d-%m")

month_name = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября",
              "декабря"][stream_date.month - 1]

draw_text(d, u"{0} {1} в {2}".format(stream_date.day, month_name, args.time), fnt[1], y)

out = Image.alpha_composite(game_image, txt)
# out.show()
output = Image.new('RGB', out.size, (0, 0, 0))
output.paste(out, out.split()[-1])
output.save(
    "{0}_{1}_{2}{3}.jpg".format(args.game.replace(' ', '_'), game_count, stream_date.month, stream_date.day))

print("Announcement saved to {0}_{1}_{2}{3}.jpg".format(args.game.replace(' ', '_'), game_count, stream_date.month,
                                                        stream_date.day))
