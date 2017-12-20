#!python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import codecs
import configparser

from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help="Config file location (default: config.ini)", dest="config",
                    default="config.ini")
parser.add_argument("game", help="Game")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.config, "utf-8")

# get an image
cover = Image.open(config[args.game]['cover']).convert('RGBA')


# cover = Image.open('Seasons.jpg').convert('RGBA')

def draw_text(d_, text, font, x_, y_):
    d_.text((x_, y_), text, font=font, fill=(255, 165, 12, 255))


def get_xy(xpos_, ypos_, xoff_, yoff_, cover_size, text_size):
    x = 0
    y = 0
    if xpos_ == "left":
        x += xoff_
    elif xpos_ == "right":
        x = cover_size[0] - text_size[0] + xoff_
    elif xpos_ == "center":
        x = (cover_size[0] - text_size[0]) / 2 + xoff_
    else:
        raise RuntimeError("Invalid pos_x value {0}".format(xpos_))

    if ypos_ == "left":
        y += yoff_
    elif ypos_ == "right":
        y = cover_size[1] - text_size[1] + yoff_
    elif ypos_ == "center":
        y = (cover_size[1] - text_size[1]) / 2 + yoff_
    else:
        raise RuntimeError("Invalid pos_y value {0}".format(ypos_))

    return x, y


txt = Image.new('RGBA', cover.size, (255, 255, 255, 0))
# get a font
fnt = [ImageFont.truetype('Purisa.ttf', 240), ImageFont.truetype('Purisa.ttf', 60)]
# get a drawing context
d = ImageDraw.Draw(txt)

Text = "# {0}".format(config[args.game]['count_yt'])

x, y = get_xy(config[args.game].get('pos_x', 'right'), config[args.game].get('pos_y', 'bottom'),
              config[args.game].get('off_x', '-20'), config[args.game].get('off_y', '-20'),
              cover.size, d.textsize(Text, font=fnt[0]))

draw_text(d, Text, fnt[0], x, y)

out = Image.alpha_composite(cover, txt)
background = Image.new('RGB', cover.size, (0, 0, 0))
background.paste(out, out.split()[-1])
background.save(background.save("{0}_{1}.jpg".format(args.game.replace(' ', '_'), config[args.game]['count_yt'])))

if config.has_option(args.game, 'count'):
    config[args.game]['count_yt'] = str(int(config[args.game]['count_yt']) + 1)
    with codecs.open(args.config, 'w', 'utf-8') as f:
        config.write(f)
