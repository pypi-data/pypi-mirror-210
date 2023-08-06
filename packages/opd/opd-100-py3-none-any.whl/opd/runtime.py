# This file is placed in the Pubic Domain.


import time


from .command import Commands
from .default import Default
from .errored import Errors
from .message import Message
from .objects import Object, kind, update
from .persist import Persist
from .utility import fntime


class Config(Default):

    pass


Cfg = Config()
Cfg.date = time.ctime(time.time()).replace("  ", " ")
Cfg.debug = False
Cfg.mod = "cmd,err,flt,mod,sts,thr,upt"
Cfg.name = "opd"


def command(cli, txt) -> Message:
    evt = cli.event(txt)
    Commands.handle(evt)
    evt.ready()
    return evt


def parse_cli(txt) -> Message:
    msg = Message()
    msg.parse(txt)
    update(Cfg, msg)
    Cfg.mod += msg.mods
    Cfg.opts = msg.opts
    Cfg.txt = msg.txt
    return Cfg
