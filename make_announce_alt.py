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
parser.add_argument('-n', '--no-advance', help="Don't advance counter (useful for initial tuning)", dest="advance",
                    action="store_false")
parser.add_argument("game", help="Game")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.config, "utf-8")

if os.name != 'posix':
    root = r"c:\Windows\Fonts"
else:
    root = "/usr/share/fonts/truetype/tlwg/"

# purisa = os.path.join(root, 'Purisa.ttf')
purisa = os.path.join('.', 'docker_one.ttf')
# print(purisa)

if not config.has_section(args.game):
    print("Game {0} not found in config file {1}".format(args.game, args.config))
    exit(0)

# get an image
# cover = Image.open('Skyrim.jpg').convert('RGBA')
# cover = Image.open('Infra.jpg').convert('RGBA')
bg_image = Image.open(config[args.game]['background']).convert('RGBA')
game_image = Image.open(config[args.game]['game']).convert('RGBA')


def draw_text(d_, text, font, yy, xx=757, color=(255, 255, 255, 255)):
    print('at', xx, yy, 'with color', color, 'text', text)
    w, h = d_.textsize(text, font=font)
    d_.text((xx, yy), text, font=font, fill=color)
    return w, h


canvas = Image.new('RGBA', bg_image.size, (255, 255, 255, 0))
canvas.paste(game_image, ((bg_image.size[0] - game_image.size[0]) - 15, 300))
# get a font
fnt = [ImageFont.truetype(purisa, 77), ImageFont.truetype(purisa, 44)]
# get a drawing context
d = ImageDraw.Draw(canvas)

line_cnt = config[args.game].get('linec', 2)
y = int(config[args.game].get('start_y', 540))
for i in range(1, int(line_cnt) + 1):
    line_h = draw_text(d, config[args.game]['line{0}'.format(i)].format(**config[args.game]), fnt[0], y)[1]
    y += line_h + int(config[args.game].get('pad_y', 10))

game_count = int(config[args.game].get('count', '1'))

if args.advance:
    config[args.game]['count'] = str(game_count + 1)

with codecs.open(args.config, 'w', 'utf-8') as f:
    config.write(f)

stream_date = datetime.datetime.strptime(args.date, "%d-%m")

month_name = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября",
              "декабря"][stream_date.month - 1]

width = draw_text(d, u"{0} {1} ".format(stream_date.day, month_name), fnt[1], 1000, 1000, (0, 0, 0, 255))[0]
print(args.time, width, 1000 + width, canvas.size[0])
draw_text(d, args.time, fnt[1], 1000 + width, 1000, (242, 54, 55, 0))

# out = Image.alpha_composite(bg_image, canvas)
out = canvas
# out.show()
output = Image.new('RGB', out.size, (0, 0, 0))
output.paste(out, out.split()[-1])
output.save(
    "{0}_{1}_{2}-{3}.jpg".format(args.game.replace(' ', '_'), game_count, stream_date.month, stream_date.day))

print("Announcement saved to {0}_{1}_{2}-{3}.jpg".format(args.game.replace(' ', '_'), game_count, stream_date.month,
                                                         stream_date.day))
