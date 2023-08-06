# This file is placed in the Public Domain.


import io
import traceback


from ..errored import Errors


## COMMANDS


def err(event):
    for ex in Errors.errors:
        stream = io.StringIO(traceback.print_exception(type(ex), ex, ex.__traceback__))
        for line in stream.readlines():
            event.reply(line)
    else:
        event.reply("no error")
