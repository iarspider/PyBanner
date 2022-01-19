#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import codecs
import configparser

from PIL import Image, ImageDraw, ImageFont, ImageColor

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help="Config file location (default: config.ini)", dest="config",
                    default="config.ini")
parser.add_argument('-n', '--no-advance', help="Don't advance counter (useful for initial tuning)", dest="advance",
                    action="store_false")
parser.add_argument("game", help="Game")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.config, "utf-8")
config_game = config[args.game]

    
index = config_game.get('count_yt', 1)

# use screenshot as a base?
screenshot = config_game.get('screenshot', None)

# get an image
if screenshot:
    cover_name = screenshot.format(index=index)
else:
    cover_name = config_game.get('cover_alt', None) or config_game.get('cover', None)
    if not cover_name:
        print("Neither cover_alt nor cover keys found in config file, unable to create banner")
        exit()

cover = Image.open(cover_name).convert('RGBA')

def get_xy(cover_size, text_size):
    xoff = int(config_game.get("off_x", '-20'))
    yoff = int(config_game.get("off_y", "-20"))

    xpos = config_game.get("pos_x", "right")
    ypos = config_game.get("pos_y", "bottom")

    x_ = 0
    y_ = 0
    if xpos == "left":
        x_ = 0
        # x_ += xoff
    elif xpos == "right":
        # x_ = 0
        x_ = cover_size[0] - text_size[0]
    elif xpos == "center":
        # x_ = 0
        x_ = (cover_size[0] - text_size[0]) / 2
    else:
        raise RuntimeError("Invalid pos_x value {0}".format(xpos))

    x_ += xoff

    if ypos == "top":
        y_ = 0
    elif ypos == "bottom":
        y_ = cover_size[1] - text_size[1]
    elif ypos == "center":
        y_ = (cover_size[1] - text_size[1]) / 2
    else:
        raise RuntimeError("Invalid pos_y value {0}".format(ypos))

    y_ += yoff

    return x_, y_


def draw_text(d_):
    prefix = config_game.get('prefix', '#').replace('{}', ' ')
    text = "{0}{1}".format(prefix, config_game.get('count_yt', 1))
    x_, y_ = get_xy(cover.size, d.textsize(text, font=fnt))
    color = ImageColor.getrgb(config_game.get('font_color', '#000000'))

    d_.text((x_, y_), text, font=fnt, fill=color)
    
    
txt = Image.new('RGBA', cover.size, (255, 255, 255, 0))
# get a font
fnt = ImageFont.truetype(config_game.get('font_name', 'Purisa.ttf'), int(config_game.get('font_size', 240)))
# fnt = ImageFont.truetype('docker_one.ttf', int(config_game.get('font_size', 177)))
# fnt = ImageFont.truetype('DejaVuSansMono-Bold.ttf', int(config_game.get('font_size', 177)))
# get a drawing context
d = ImageDraw.Draw(txt)
draw_text(d)

out = Image.alpha_composite(cover, txt)
background = Image.new('RGB', cover.size, (0, 0, 0))
background.paste(out, out.split()[-1])
fname = "{0}_{1}.jpg".format(args.game.replace(' ', '_'), config_game.get('count_yt', 1))
background.save(fname)
print("Banner saved to", fname)

if args.advance:
    config_game['count_yt'] = str(int(config_game.get('count_yt', 1)) + 1)

    with codecs.open(args.config, 'w', 'utf-8') as f:
        config.write(f)
