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


def get_xy(xpos, ypos, xoff, yoff, cover_size, text_size):
    x_ = 0
    y_ = 0
    if xpos == "left":
        x_ += xoff
    elif xpos == "right":
        x_ = cover_size[0] - text_size[0] + xoff
    elif xpos == "center":
        x_ = (cover_size[0] - text_size[0]) / 2 + xoff
    else:
        raise RuntimeError("Invalid pos_x value {0}".format(xpos))

    if ypos == "left":
        y_ += yoff
    elif ypos == "right":
        y_ = cover_size[1] - text_size[1] + yoff
    elif ypos == "center":
        y_ = (cover_size[1] - text_size[1]) / 2 + yoff
    else:
        raise RuntimeError("Invalid pos_y value {0}".format(ypos))

    return x_, y_


txt = Image.new('RGBA', cover.size, (255, 255, 255, 0))
# get a font
fnt = [ImageFont.truetype('Purisa.ttf', 240), ImageFont.truetype('Purisa.ttf', 60)]
# get a drawing context
d = ImageDraw.Draw(txt)

Text = "# {0}".format(config[args.game]['count_yt'])

x, y = get_xy(config[args.game].get('pos_x', 'right'), config[args.game].get('pos_y', 'bottom'),
              int(config[args.game].get('off_x', '-20')), int(config[args.game].get('off_y', '-20')),
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
