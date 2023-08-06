# This file is placed in the Public Domain.


from ..command import Commands


## COMMANDS


def cmd(event):
    event.reply(','.join(sorted(Commands.cmds)))
