# This file is placed in the Public Domain.


import queue
import ssl
import threading


from .errored import Errors
from .objects import Object
from .message import Message
from .threads import launch


class Handler(Object):

    def __init__(self):
        Object.__init__(self)
        self.cbs = Object()
        self.queue = queue.Queue()
        self.stopped = threading.Event()
        self.register('command', self.handle)

    @staticmethod
    def dispatch(func, evt):
        try:
            func(evt)
        except Exception as ex:
            exc = ex.with_traceback(ex.__traceback__)
            Errors.errors.append(exc)
            evt.ready()

    def event(self, txt):
        msg = Message()
        msg.type = 'command'
        msg.orig = repr(self)
        msg.parse(txt)
        return msg

    def handle(self, evt):
        func = getattr(self.cbs, evt.type, None)
        if func:
            evt._thr = launch(self.dispatch, func, evt, name=evt.cmd)
        return evt

    def loop(self):
        while not self.stopped.is_set():
            try:
                self.handle(self.poll())
            except (ssl.SSLError, EOFError, KeyboardInterrupt) as ex:
                Errors.handle(ex)
                self.restart()

    def one(self, txt):
        return self.handle(self.event(txt))

    def poll(self):
        return self.queue.get()

    def put(self, evt):
        self.queue.put_nowait(evt)

    def register(self, cmd, func):
        setattr(self.cbs, cmd, func)

    def restart(self):
        self.stop()
        self.start()

    def start(self):
        launch(self.loop)

    def stop(self):
        self.stopped.set()
        self.queue.put_nowait(None)
