#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import collections.abc
import copy
import datetime
import os

import yaml
from PIL import Image, ImageDraw, ImageFont
from pytz import timezone

VERSION = 3


# source: https://stackoverflow.com/a/3233356/2652987
def update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


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


def draw_text(d_, text, font, yy, xx, color=(255, 255, 255, 255)):
    bbox = d_.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    d_.text((xx, yy), text, font=font, fill=color)
    return width, height


def make_announce(config, config_season, stream_date, stream_time_str):
    background = Image.open(config['background']).convert('RGBA')

    logo = Image.open(config['logo']['file'])
    offset_x = config['logo']['offset']['x']
    offset_y = config['logo']['offset']['y']
    background.paste(logo, ((background.size[0] - logo.size[0]) - offset_x, offset_y))

    purisa = os.path.join('.', 'docker_one.ttf')
    fnt = [ImageFont.truetype(purisa, 60), ImageFont.truetype(purisa, 50)]

    canvas = ImageDraw.ImageDraw(background)
    x = 757 + config['text']['offset']['x']
    y = 540 + config['text']['offset']['y']
    pad_y = config['text']['padding']
    for line in config['text']['lines']:
        if line.startswith('_'):
            this_font = fnt[1]
            line = line[1:]
        else:
            this_font = fnt[0]

        count = config['index']
        season = config_season['index']
        scount = config['index'] + config_season['offset']
        h = draw_text(canvas, line.format(count=count, season=season, scount=scount), this_font, y, x)[1]
        y += h + pad_y

    month_name = \
        ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября",
         "декабря"][stream_date.month - 1]
    date_text = u"{0} {1} ".format(stream_date.day, month_name)

    width, height = draw_text(canvas, date_text, fnt[0], xx=850, yy=1000, color=(0, 0, 0, 255))
    draw_text(canvas, stream_time_str, fnt[0], xx=850 + width, yy=1000, color=(242, 54, 55, 255))

    out = Image.new('RGB', background.size, (0, 0, 0))
    out.paste(background)
    return out, scount


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="Config file location (default: config.ini)", dest="config",
                        default="config.yaml")
    parser.add_argument('-d', '--date', help="Stream date, default today, format DD-MM or DD-MM-YYYY", dest="date",
                        default=datetime.datetime.now().strftime("%d-%m-%Y"))
    parser.add_argument('-t', '--time', help="Stream time (default taken from config)", dest="time", default=None)
    parser.add_argument('--dest-time', help="Stream time is in target time zone. Requires `-t`",
                        action='store_true')
    parser.add_argument('-n', '--no-advance', help="Don't advance counter (useful for initial tuning)", dest="advance",
                        action="store_false")
    parser.add_argument('-i', '--index', help="Stream number (implies -n)", dest='index', default=-1, type=int)
    parser.add_argument("--amend", help="Update previous announce (implies -n)", dest="amend", action="store_true")
    parser.add_argument("game", help="Game")
    args = parser.parse_args()
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
    if args.index > 0:
        config_game['announce']['index'] = args.index

    local_tz = timezone(config['global']['time']['from'])
    target_tz = timezone(config['global']['time']['to'])

    if len(args.date.split('-')) == 2:
        args.date = args.date + '-2021'
    try:
        stream_date = datetime.datetime.strptime(args.date, "%d-%m-%Y")
    except ValueError:
        stream_date = datetime.datetime.now()

    stream_date = stream_date.date()

    stream_time = None  # stream_time is used ONLY for timezone conversion, the actual time is always in args.time
    special_time = False
    if args.time is not None:
        if ':' not in args.time:
            if args.time.lower() == 'zth':
                args.time = '"После Зига" (тм)'
                special_time = True
            elif args.time.lower() == 'prayda':
                args.time = '"После Лисы" (тм)'
                special_time = True
            elif args.time.lower() == 'moar':
                args.time = '"После Е-нота" (тм)'
                special_time = True
        else:
            stream_time = datetime.datetime.strptime(args.time, "%H:%M").time()
    else:
        if args.dest_time:
            print("WARNING: --dest-time ignored!")
            args.dest_time = False

        stream_time = datetime.datetime.strptime(config['global']['time']['time'], "%H:%M").time()

    if stream_time is None:
        stream_time = datetime.time(12, 0)

    stream_datetime = datetime.datetime.combine(stream_date, stream_time)
    stream_datetime = local_tz.localize(stream_datetime).astimezone(target_tz)
    if not special_time:
        args.time = stream_datetime.strftime("%H:%M") + ' МСК'

    if args.index > 0 or args.amend:
        args.advance = False

    if args.index > 0 and args.amend:
        raise RuntimeError("Can't use -i/--index together with --amend!")

    if args.amend:
        config_game["announce"]["index"] = max(0, config_game["announce"]["index"] - 1)

    announce, index = make_announce(config_game['announce'], config_game['season'], stream_datetime, args.time)

    fname = "{0}_{1}_{2:02d}{3:02d}.jpg".format(args.game.replace(' ', '_'), index,
                                                stream_date.month, stream_date.day)
    announce.save(fname)

    print("Announcement saved to", fname)

    if args.advance:
        config[args.game]['announce']['index'] = config_game['announce']['index'] + 1

        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(dict(config), stream=f, encoding='utf-8', allow_unicode=True, sort_keys=False)


if __name__ == '__main__':
    main()
