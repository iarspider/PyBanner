#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import os
import yaml
import collections.abc
import copy

from PIL import Image, ImageDraw, ImageFont, ImageColor
import numpy as np

VERSION = 3

# source: https://stackoverflow.com/a/3233356/2652987
def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

# source: https://note.nkmk.me/en/python-numpy-generate-gradation-image/
def get_gradient_2d(start, stop, width, height, is_horizontal):
    if is_horizontal:
        return np.tile(np.linspace(start, stop, width), (height, 1))
    else:
        return np.tile(np.linspace(start, stop, height), (width, 1)).T


# source: https://note.nkmk.me/en/python-numpy-generate-gradation-image/
def get_gradient_3d(width, height, start_list, stop_list, is_horizontal_list):
    result = np.zeros((height, width, len(start_list)), dtype=np.single)

    for i, (start, stop, is_horizontal) in enumerate(zip(start_list, stop_list, is_horizontal_list)):
        result[:, :, i] = get_gradient_2d(start, stop, width, height, is_horizontal)

    return result

# source: https://www.oreilly.com/library/view/python-cookbook/0596001673/ch03s24.html
def int_to_roman(input):
    """ Convert an integer to a Roman numeral. """

    if not isinstance(input, type(1)):
        raise TypeError("expected integer, got %s" % type(input))
    if not 0 < input < 4000:
        raise ValueError("Argument must be between 1 and 3999")
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
    result = []
    for i in range(len(ints)):
        count = int(input / ints[i])
        result.append(nums[i] * count)
        input -= ints[i] * count
    return ''.join(result)

def format_label(config: dict, season: dict, index, part):
    format_ = config['text'].get('format', None)
    roman = config['text'].get('roman', False)
    index = index or config.get('index', 1)
    sindex = index + int(season['offset'])
    season_ = season.get('index', 1)

    if roman:
        text = int_to_roman(index)
    else:
        if format_ is None:
            prefix = config['text'].get('prefix', '#')
            if prefix == '#' and season['index'] > 0:
                prefix = f"#{season['index']}×"

            if sindex != index:
                suffix = f" ({sindex})"
            else:
                suffix = ""
                
            if part:
                suffix = f"{suffix}.{part}"

            text = "{0}{1}{2}".format(prefix, index, suffix)
        else:
            text = format_.format(index=index, sindex=sindex, season=season_, part=part)

    return text, sindex


def get_xy(config: dict, cover_size: tuple, text_dim: tuple):
    """
    Convert relative position of text to actual position
    (i.e. resolve 'right', 'bottom', offsets)

    :param config: label position
    :param cover_size: Overall image size
    :param text_dim: Text dimensions
    :return: calculated text position
    """
    xoff = config['padding']['x']
    yoff = config['padding']['y']

    xpos = config['position']['x']
    ypos = config['position']['y']

    x_ = 0
    y_ = 0
    if xpos == "left":
        x_ = 0
        # x_ += xoff
    elif xpos == "right":
        # x_ = 0
        x_ = cover_size[0] - text_dim[0]
    elif xpos == "center":
        # x_ = 0
        x_ = (cover_size[0] - text_dim[0]) / 2
    else:
        raise RuntimeError("Invalid pos_x value {0}".format(xpos))

    x_ += xoff

    if ypos == "top":
        y_ = 0
    elif ypos == "bottom":
        y_ = cover_size[1] - text_dim[1]
    elif ypos == "center":
        y_ = (cover_size[1] - text_dim[1]) / 2
    else:
        raise RuntimeError("Invalid pos_y value {0}".format(ypos))

    y_ += yoff

    return x_, y_


def draw_text(config: dict, img: Image.Image, fnt: ImageFont.ImageFont, text):
    """
    Draw episode label (simple, no gradient)

    :param config: label parameters (prefix, font_color)
    :param img: Image to draw on
    :param fnt: font to use
    :param text: label to draw

    :return: nothing
    """
    txt = Image.new('RGBA', img.size, (255, 255, 255, 0))
    d_ = ImageDraw.ImageDraw(txt)
    bbox = d_.textbbox((0, 0), text, font=fnt)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    x_, y_ = get_xy(config['text'], txt.size, (width, height))
    color = ImageColor.getrgb(config['text']['font']['color'][0])

    d_.text((x_, y_), text, font=fnt, fill=color)
    img.alpha_composite(txt)


def draw_text_gradient(config: dict, img: Image.Image, fnt: ImageFont.ImageFont, text):
    """
    Draw episode label (with gradient)

    :param config: label parameters (prefix, font, ...)
    :param img: image to draw on
    :param fnt: font to use
    :param text: label to draw

    :return: nothing
    """
    canvas = Image.new('RGBA', img.size, (255, 255, 255, 0))
    d_ = ImageDraw.ImageDraw(canvas)

    bbox = d_.textbbox((0, 0), text, font=fnt)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    img_xy = get_xy(config['text'], img.size, (text_w, text_h))

    color_1 = ImageColor.getrgb(config['text']['font']['color'][0])
    color_2 = ImageColor.getrgb(config['text']['font']['color'][1])
    direction = config['text']['font']['gradient'] == 'horizontal'

    grad = Image.fromarray(
        np.uint8(get_gradient_3d(text_w, text_h, color_1, color_2, (direction, direction, direction))))
    alpha = Image.new('L', (text_w, text_h))
    draw = ImageDraw.Draw(alpha)
    draw.text((0, 0), text, fill='white', font=fnt)
    grad.putalpha(alpha)

    canvas.paste(grad, img_xy)
    img.alpha_composite(canvas)


def make_banner(game, config, season, label, index, archive, part):
    if archive:
        bgfn = os.path.join("archive", config['background'])
    else:
        bgfn = config['background']
    
    background = Image.open(bgfn).convert('RGBA')
    canvas = Image.new('RGBA', background.size, (255, 255, 255, 0))
    if config['screenshot'] != '':
        screenshot_name = config['screenshot'].format(index=index)
        screenshot = Image.open(screenshot_name).convert('RGBA')
        canvas.paste(screenshot)
        canvas.alpha_composite(background)
    else:
        canvas.paste(background)

    fnt = ImageFont.truetype(config['text']['font']['name'], config['text']['font']['size'])

    label, sindex = (label.format(part), 0) if label else format_label(config, season, int(index), part)

    if config['text']['font']['color'][0] != config['text']['font']['color'][1]:
        draw_text_gradient(config, canvas, fnt, label)
    else:
        draw_text(config, canvas, fnt, label)

    out = Image.new('RGB', canvas.size, (0, 0, 0))
    out.paste(canvas)
    return out, sindex


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="Config file location (default: config.ini)", dest="config",
                        default="config.yaml")
    parser.add_argument('-a', '--archive', help="Look inside 'archive' folder'", dest="archive", action="store_true")
    parser.add_argument('-n', '--no-advance', help="Don't advance counter (useful for initial tuning)", dest="advance",
                        action="store_false")
    parser.add_argument('-l', '--label', help="Alternative label text (requires -i)", dest="label", default=None)
    parser.add_argument('-i', '--index', help="Force episode index. Implies -n", dest="index", default=None)
    parser.add_argument('--parts', help="Set number of parts", dest="parts", default=None)
    parser.add_argument("game", help="Game")
    args = parser.parse_args()

    if args.label is not None:
        args.label = args.label.replace(' 1/2', '½')
        args.label = args.label.replace(' 3/4', '¾')
        args.label = args.label.replace(' 5/6', '⅚')
        if args.index is None:
            print('ERROR: --label requires --index, quitting...')

    if args.index is not None:
        args.advance = False
        print('WARNING: Setting no-advance flag because --index was requested')

    with open(args.config, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if config['global']['version'] != VERSION:
        raise RuntimeError(
            f"Config file created with different version (expected {VERSION}, got "
            f"{config['global']['version']})!")

    config_update = config.get(args.game, None)
    if config_update is None:
        print(f"Configuration for {args.game} not found!")
        exit(1)

    config_game = copy.deepcopy(config['default'])
    update(config_game, config_update)

    index = args.index or config_game['cover']['index']
    if not args.parts:
        banner, sindex = make_banner(args.game, config_game['cover'], config_game['season'], args.label, index, args.archive, None)
        index = args.index or sindex

        fname = "{0}_{1}.jpg".format(args.game.replace(' ', '_'), index)
        banner.save(fname)
        print("Banner saved to", fname)
    else:
        for part_i in range(1, int(args.parts)+1):
            banner, sindex = make_banner(args.game, config_game['cover'], config_game['season'], args.label, index, args.archive, part_i)
            oindex = args.index or sindex

            fname = "{0}_{1}p{2}.jpg".format(args.game.replace(' ', '_'), oindex, part_i)
            banner.save(fname)
            print("Banner saved to", fname)

    if args.advance:
        index = args.index or config[args.game]['cover']['index']
        config[args.game]['cover']['index'] = index + 1

        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(dict(config), stream=f, encoding='utf-8', allow_unicode=True, sort_keys=False)


if __name__ == '__main__':
    main()
