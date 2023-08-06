# This file is placed in the Public Domain.


"there are no paths"


import os
import sys
import termios
import time
import traceback


from .clients import Client
from .command import Commands
from .errored import Errors
from .loggers import Logging
from .objects import update
from .persist import Persist, write
from .runtime import DATE, Cfg, command, launch, parse_cli
from .utility import spl


import opd.modules


Persist.workdir = os.path.expanduser(f"~/.{Cfg.name}")


def cprint(txt):
    print(txt)
    sys.stdout.flush()


class CLI(Client):

    def announce(self, txt):
        pass

    def raw(self, txt):
        cprint(txt)


class Console(CLI):

    def handle(self, evt):
        CLI.handle(self, evt)
        evt.wait()

    def poll(self):
        return self.event(input("> "))


## UTILITY


def banner():
    cprint(f"{Cfg.name.upper()} started at {DATE}")
    

def daemon():
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    os.setsid()
    os.umask(0)
    sis = open('/dev/null', 'r')
    os.dup2(sis.fileno(), sys.stdin.fileno())
    sos = open('/dev/null', 'a+')
    ses = open('/dev/null', 'a+')
    os.dup2(sos.fileno(), sys.stdout.fileno())
    os.dup2(ses.fileno(), sys.stderr.fileno())


def scanstr(mods, init=None, doall=False) -> None:
    res = []
    if doall:
        mods = ",".join(opd.modules.__all__)
    for modname in spl(mods):
        mod = getattr(opd.modules, modname)
        if not mod:
            continue
        Commands.scan(mod)
        if init and "start" in dir(mod):
            mod._thr = launch(mod.start)
        res.append(mod)
    return res


def waiter():
    got = []
    for ex in Errors.errors:
        traceback.print_exception(type(ex), ex, ex.__traceback__)
        got.append(ex)
    for exc in got:
        Errors.errors.remove(exc)


def wrap(func):
    fds = sys.stdin.fileno()
    gotterm = True
    try:
        old = termios.tcgetattr(fds)
    except termios.error:
        gotterm = False
    try:
        func()
    except (EOFError, KeyboardInterrupt):
        print('')
    finally:
        if gotterm:
            termios.tcsetattr(fds, termios.TCSADRAIN, old)
        waiter()


## RUNTIME


def main():
    parse_cli(' '.join(sys.argv[1:]))
    if "v" in Cfg.opts and "d" not in Cfg.opts:
        Logging.debug = cprint
        banner()
    dowait = False
    if Cfg.txt:
        scanstr(Cfg.mod, "a" in Cfg.opts)
        cli = CLI()
        command(cli, Cfg.otxt)
    elif 'd' in Cfg.opts:
        daemon()
        dowait = True
    if "c" in Cfg.opts:
        dowait = True
    if dowait:
        scanstr(Cfg.mod, True)
        if 'c' in Cfg.opts and "d" not in Cfg.opts:
            csl = Console()
            csl.start()
        while 1:
            time.sleep(1.0)
            waiter()


if __name__ == "__main__":
    wrap(main)
