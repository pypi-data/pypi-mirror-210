# This file is placed in the Public Domain.


import threading


from .default import Default
from .listens import Listens
from .parsers import parse
from .utility import spl


class Message(Default):

    __slots__ = ('_ready', '_thr')

    def __init__(self, *args, **kwargs):
        Default.__init__(self, *args, **kwargs)
        self._ready = threading.Event()
        self._thr = None
        self.result = []

    def parse(self, txt):
        parse(self, txt)

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self.result.append(txt)

    def show(self):
        for txt in self.result:
            Listens.say(self.orig, txt, self.channel)

    def wait(self):
        if self._thr:
            self._thr.join()
        self._ready.wait()
        return self._result
