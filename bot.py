#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import functools
import json
from threading import Thread

import requests

DEF_TOKEN = '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'

class Bot(Thread):
    """
    Worker of one telegram bot
    """
    def __init__(self, token=DEF_TOKEN, master_id=0, updater=None):
        super().__init__()
        self.token = token
        self.active = None
        self.master_id = None
        self.username = None
        self.first_name = None
        self.input = collections.deque()
        self.input_offset = None
        self.updater = updater
        info = self.raw_method_request('getMe')

        if not info['ok'] or not info['result']['is_bot']:
            return

        self.active = True
        self.master_id = master_id
        self.username = info['result']['username']
        self.first_name = info['result']['first_name']

    def run(self):
        """
        start Thread
        """
        while self.active:
            while self.input:
                self.updater(self, self.input.popleft())
            self.get_updates()

    def raw_method_request(self, method, **kvargs):
        """
        Request method by name with args
        Returning dict
        """
        response = requests.get('https://api.telegram.org/bot{}/{}'.format(self.token, method), data=kvargs)
        return response.json()

    def get_updates(self, limit=None):
        """
        Return limit update
        """
        info = self.raw_method_request('getUpdates',
                                       limit=limit,
                                       timeout=60,
                                       offset=self.input_offset,
                                       allowed_updates=['message'])
        if info['ok']:
            self.input.extend(info['result'])
            self.input_offset = self.input[-1]['update_id'] + 1 if self.input else self.input_offset
