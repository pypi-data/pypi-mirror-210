# This file is placed in the Public Domain.


import time


from ..utility import elapsed


starttime = time.time()


def upt(event):
    event.reply(elapsed(time.time()-starttime))
