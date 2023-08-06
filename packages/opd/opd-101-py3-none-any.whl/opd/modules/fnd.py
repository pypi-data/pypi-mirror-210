# This file is placed in the Public Domain.


import time


from ..objects import keys
from ..objfunc import prt
from ..persist import Persist
from ..utility import elapsed, fntime


## COMMANDS


def fnd(event):
    if not event.args:
        res = ','.join(sorted([x.split('.')[-1].lower() for x in Persist.files()]))
        if res:
            event.reply(res)
        else:
            event.reply('no types yet.')
        return
    otype = event.args[0]
    nmr = 0
    keyz = None
    if event.gets:
        keyz = ','.join(keys(event.gets))
    if len(event.args) > 1:
        keyz += ',' + ','.join(event.args[1:])
    for obj in Persist.find(otype, event.gets):
        if not keyz:
            keyz = ',' + ','.join(keys(obj))
        prnt = prt(obj, keyz)
        lap = elapsed(time.time()-fntime(obj.__oid__))
        event.reply(f'{nmr} {prnt} {lap}')
        nmr += 1
    if not nmr:
        event.reply(f'no result ({event.txt})')
