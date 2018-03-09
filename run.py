#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import time

import bot
import log


def crate_arg_parser():
    """
    Make parser object for console arguments
    """
    arg_parser = argparse.ArgumentParser(description='censorbot starting')
    arg_parser.add_argument('token',
                            metavar='TOKEN',
                            type=str,
                            nargs='?',
                            help='Access token for api.telegram.org/bot like {}'.format(bot.DEF_TOKEN),
                            default=bot.DEF_TOKEN)
    arg_parser.add_argument('boss_id',
                            metavar='ID',
                            type=int,
                            nargs='?',
                            help='Chat ID of admin',
                            default=0)
    return arg_parser

def my_log(lobj):
    """
    My log function
    """
    print(lobj)

LOG = log.Logger(my_log)

def stiker(inp):
    print (str(inp))
    print(inp['message']['sticker']['set_name'])

@LOG.logging
def process_input(bot, inp):
    """
    Тестовый обработчик
    """
    if stiker(inp):
        bot.raw_method_request('sendMessage',
                               chat_id=inp['message']['chat']['id'],
                               text='стикер Вшлеме',
                               reply_to_message_id=inp['message']['message_id'])



def main():
    """
    Main
    """
    parser = crate_arg_parser()
    args = parser.parse_args()
    my_bot = bot.Bot(args.token, args.boss_id, process_input)
    my_bot.start()
    time.sleep(30)
    my_bot.active = False

if __name__ == "__main__":
    LOG.start()
    main()
    LOG.join()
