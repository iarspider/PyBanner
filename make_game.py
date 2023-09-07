#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import copy
import os

import yaml

VERSION = 3

def guess_name(game, announce):
    res = ''
    found = False
    for suffix in {True: ('-cover', '-small'), False: ('-banner', '-big')}[announce]:
        for ext in ('.jpg', '.jpeg'):
            res = game + suffix + ext
            if os.path.exists(res):
                found = True
                break
            else:
                res = ''
        if found:
            break
            
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="Config file location (default: config.ini)", dest="config",
                        default="config.yaml")
    parser.add_argument('-a', '--announce', metavar='FILE', dest='announce', help='Image to use for announcements',
                        default=None)
    parser.add_argument('-b', '--banner', metavar='FILE', dest='banner', help='Image to use for banners',
                        default=None)
    parser.add_argument('-t', '--text', help='Text for cover; use # to separate lines')
    parser.add_argument("game", help="Game")
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if config['global']['version'] != VERSION:
        raise RuntimeError(
            f"Config file created with different version (expected {VERSION}, got "
            f"{config['global']['version']})!")

    config_update = config.get(args.game, None)
    if config_update is not None:
        print(f"Configuration for {args.game} already present, quitting!")
        exit(1)

    config_game = copy.deepcopy(config['template'])

    args.announce = args.announce or guess_name(args.game, True)

    args.banner = args.banner or guess_name(args.game, False)

    if os.path.exists(args.announce):
        config_game['announce']['logo']['file'] = args.announce
    else:
        print('[WARN] Cover image {0} not found'.format(args.announce))

    if os.path.exists(args.banner):
        config_game['cover']['background'] = args.banner
    else:
        print('[WARN] Banner image {0} not found'.format(args.banner))

    if args.text:
        config_game['announce']['text']['lines'] = args.text.split('#')

    # yaml.dump(config_game, stream=sys.stdout, allow_unicode=True)
    config[args.game] = config_game
    with open('config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(dict(config), stream=f, encoding='utf-8', allow_unicode=True, sort_keys=False)

    os.startfile(args.config, 'open')


if __name__ == '__main__':
    main()
