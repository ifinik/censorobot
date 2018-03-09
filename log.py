#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Wrap for custom logs
"""
# built-in
import collections
import datetime
import functools
import inspect
import json
import threading
import traceback
# pip3
import pytz


class JsonRepr:
    """
    Сan serialize itself
    """
    @classmethod
    def json(cls, obj, ready=dict()): #pylint: disable=W0102
        """
        Convert to json string with Circular reference control
        only for not native types
        """
        ido = id(obj)
        if ido in ready:
            result = ready[ido]
            ready.clear()
            ready[ido] = result
            return result

        ready[ido] = '__recursive__'
        result = str(obj)
        ready[ido] = result
        return result

    def __str__(self):
        return json.dumps(self.__dict__, default=self.json, ensure_ascii=False, sort_keys=True, indent=4)


class Log(JsonRepr):
    """
    Object of one log
    """
    def __init__(self, msg, log_level='log', logger=None, stack_lvl=1):
        self.msg = msg
        self.log_level = log_level
        self.logger = logger
        # list of name function from call stack
        self.stack = [lvl[3] for i, lvl in enumerate(inspect.stack()) if i > stack_lvl]
        self.exc = None
        self.start = datetime.datetime.now(pytz.utc)
        self.end = None

    def __enter__(self):
        return self

    def __exit__(self, _exctype, excinst, _exctb):
        self.end = datetime.datetime.now(pytz.utc)

        if excinst:
            self.exc = '{}\n{}'.format(excinst, traceback.format_exc())

        if isinstance(self.logger, Logger):
            self.logger.log(self, log_level='log')


class Logger(JsonRepr, threading.Thread):
    """
    Login Thread object for async log what and how you need
    """
    def __init__(self, log_func, log_init=None, log_levels=('log', 'warn', 'err'), log_level='log'):
        self.log_func = log_func
        self.log_init = log_init
        if log_init:
            self.log_init = log_init(self)
        self.log_levels = set()

        for lvl in log_levels:
            if not self.log_levels:
                if lvl == log_level:
                    self.log_levels.add(lvl)
                    continue
            self.log_levels.add(lvl)

        self.log_levels = log_levels
        self.active = True
        self.actions = collections.deque()
        self.act_rlock = threading.RLock()
        super().__init__()

    def run(self):
        while self.active:
            with self.act_rlock:
                act = self.actions.popleft() if self.actions else None
            if act:
                self.log_func(act)

    def join(self, timeout=None):
        """
        Waits until the last logs are processed and stops the thread object
        """
        self.active = False
        super().join(timeout)

    def log(self, msg, log_level='log'):
        """
        Add msg to log queue
        """
        if log_level not in self.log_levels:
            return

        if not isinstance(msg, Log):
            msg = Log(msg, log_level=log_level)
        else:
            msg.logger = None

        with self.act_rlock:
            self.actions.append(msg)

    def logging(self, func, label='', log_level='log', stack_lvl=1):
        """
        Wrapper for loging function call
        """
        @functools.wraps(func)
        def inner(*args, **kvargs):
            """
            Log wrapper
            """
            act = dict(input=(args, kvargs),
                       label=label,
                       output=None)
            with Log(act, log_level, self, stack_lvl+2):
                result = func(*args, **kvargs)
                act['output'] = result
        return inner
