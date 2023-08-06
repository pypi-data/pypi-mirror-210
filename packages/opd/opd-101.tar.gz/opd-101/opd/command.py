# This file is placed in the Public Domain.


import inspect


from .errored import Errors
from .objects import Object
from .message import Message
from .utility import spl


def __dir__():
    return (
            'Commands',
           )


class Commands(Object):

    cmds = Object()

    @staticmethod
    def add(cmd, func) -> None:
        setattr(Commands.cmds, cmd, func)

    @staticmethod
    def handle(evt) -> Message:
        evt.parse(evt.txt)
        func = getattr(Commands.cmds, evt.cmd, None)
        if func:
            try:
                func(evt)
                evt.show()
            except Exception as ex:
                Errors.handle(ex)
        evt.ready()
        return evt

    @staticmethod
    def scan(mod) -> None:
        for _key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if 'event' in cmd.__code__.co_varnames:
                Commands.add(cmd.__name__, cmd)
