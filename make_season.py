#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import os

import yaml

VERSION = 3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="Config file location (default: config.ini)", dest="config",
                        default="config.yaml")
    parser.add_argument('-T', '--text', help='Update last line of announcement text', action='store_true',
                        dest='update_text')
    parser.add_argument("game", help="Game")
    args = parser.parse_args()

    with open(args.config, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if config['global']['version'] != VERSION:
        raise RuntimeError(
            f"Config file created with different version (expected {VERSION}, got "
            f"{config['global']['version']})!")

    config_game = config.get(args.game, None)
    if config_game is None:
        print(f"Configuration for {args.game} not present, quitting!")
        exit(1)

    if 'season' not in config_game:
        config_game['season'] = copy.deepcopy(config['default']['season'])

    config_game['season']['index'] += 1
    config_game['season']['offset'] = config_game['announce']['index'] - 1
    config_game['announce']['index'] = 1

    if args.update_text:
        config_game['announce']['text'][-1] = 'Сезон {season}, стрим {count} ({scount})'

    with open('config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(dict(config), stream=f, encoding='utf-8', allow_unicode=True, sort_keys=False)


if __name__ == '__main__':
    main()
