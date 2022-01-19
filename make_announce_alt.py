#!python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import codecs
import configparser
import datetime
import os

from PIL import Image, ImageDraw, ImageFont, ImageColor

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help="Config file location (default: config.ini)", dest="config",
                    default="config.ini")
parser.add_argument('-d', '--date', help="Stream date, default today, format DD-MM", dest="date",
                    default=datetime.datetime.now().strftime("%d-%m"))
parser.add_argument('-t', '--time', help="Stream time, default 19:00", dest="time", default="19:00")
parser.add_argument('-n', '--no-advance', help="Don't advance counter (useful for initial tuning)", dest="advance", action="store_false")
parser.add_argument('-i', '--index', help="Stream number (implies -n)", dest='index', default=-1, type=int)
parser.add_argument("game", help="Game")
args = parser.parse_args()

if ':' not in args.time:
    if args.time.lower() == 'zth':
        args.time = '"После Зига"(тм)'
    elif args.time.lower() == 'prayda':
        args.time = '"После Лисы" (тм)'

if args.index > 0:
    args.advance = False

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
game = Image.open(config[args.game]['game']).convert('RGBA')
background = Image.open(config[args.game]['background']).convert('RGBA')


def draw_text(d_, text, font, yy, xx=757, color=(255, 255, 255, 255)):
    global label_max_width
    width, height = d_.textsize(text, font=font)
    d_.text((xx, yy), text, font=font, fill=color)
    return width, height

canvas = Image.new('RGBA', background.size, (255, 255, 255, 0))
canvas.paste(game, ((background.size[0] - game.size[0]) - int(config[args.game].get('image_x', 15)), int(config[args.game].get("image_y", "300"))))
# get a font
fnt = [ImageFont.truetype(purisa, 60), ImageFont.truetype(purisa, 40)]

# get a drawing context
d = ImageDraw.Draw(canvas)

line_cnt = config[args.game].get('linec', 2)
y = int(config[args.game].get('start_y', 540))
for i in range(1, int(line_cnt)+1):
    h = draw_text(d, config[args.game]['line{0}'.format(i)].format(**config[args.game]), fnt[0], yy=y)[1]
    y += h + int(config[args.game].get('pad_y', 10))

game_count = int(config[args.game].get('count', '1')) if args.index < 0 else args.index

if args.advance:
    config[args.game]['count'] = str(game_count + 1)

    with codecs.open(args.config, 'w', 'utf-8') as f:
        config.write(f)

try:
    stream_date = datetime.datetime.strptime(args.date, "%d-%m")

    month_name = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября",
                  "декабря"][stream_date.month - 1]
    date_text = u"{0} {1} ".format(stream_date.day, month_name)
except ValueError:
    date_text = args.date
    stream_date = datetime.datetime.now()

width, height = draw_text(d, date_text, fnt[0], xx=850, yy=1000, color=(0, 0, 0, 255))
# print (width, 1000+width, game.size[0])
draw_text(d, args.time, fnt[0], xx=850+width, yy=1000, color=(242, 54, 55, 255))
#draw_text(d, args.time, fnt[1], xx=0, yy=0, color=(242, 54, 55, 255))

temp = Image.alpha_composite(background, canvas)
# out.show()
out = Image.new('RGB', temp.size, (0, 0, 0))
out.paste(temp, temp.split()[-1])
out.save("{0}_{1}_{2:02d}{3:02d}.jpg".format(args.game.replace(' ', '_'), game_count, stream_date.month, stream_date.day))

print("Announcement saved to {0}_{1}_{2:02d}{3:02d}.jpg".format(args.game.replace(' ', '_'), game_count, stream_date.month, stream_date.day))
