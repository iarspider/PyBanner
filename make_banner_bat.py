#!python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import codecs
import configparser

from PIL import Image, ImageDraw, ImageFont, ImageColor

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help="Config file location (default: config.ini)", dest="config",
                    default="config.ini")
parser.add_argument("game", help="Game")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.config, "utf-8")
config_game = config[args.game]

# get an image
conver_name = config_game.get('cover_alt', None) or config_game.get('cover')
cover = Image.open(conver_name).convert('RGBA')


# cover = Image.open('Seasons.jpg').convert('RGBA')


def get_xy(cover_size, text_size):
    xoff = int(config_game.get("off_x", '-20'))
    yoff = int(config_game.get("off_y", "-20"))

    xpos = config_game.get("pos_x", "right")
    ypos = config_game.get("pos_y", "bottom")

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

    if ypos == "top":
        y_ += yoff
    elif ypos == "bottom":
        y_ = cover_size[1] - text_size[1] + yoff
    elif ypos == "center":
        y_ = (cover_size[1] - text_size[1]) / 2 + yoff
    else:
        raise RuntimeError("Invalid pos_y value {0}".format(ypos))

    return x_, y_


def draw_text(d_):
    text = "#{0}".format(config_game['count_yt'])
    x_, y_ = get_xy(cover.size, d.textsize(text, font=fnt))
    color = ImageColor.getrgb(config_game.get('font_color', '#000000'))

    d_.text((x_, y_), text, font=fnt, fill=color)


txt = Image.new('RGBA', cover.size, (255, 255, 255, 0))
# get a font
fnt = ImageFont.truetype('Purisa.ttf', int(config_game.get('font_size', 240)))
# get a drawing context
d = ImageDraw.Draw(txt)

draw_text(d)

out = Image.alpha_composite(cover, txt)
background = Image.new('RGB', cover.size, (0, 0, 0))
background.paste(out, out.split()[-1])
background.save("{0}_{1}.jpg".format(args.game.replace(' ', '_'), config_game['count_yt']))

if config.has_option(args.game, 'count'):
    config_game['count_yt'] = str(int(config_game['count_yt']) + 1)
    with codecs.open(args.config, 'w', 'utf-8') as f:
        config.write(f)
