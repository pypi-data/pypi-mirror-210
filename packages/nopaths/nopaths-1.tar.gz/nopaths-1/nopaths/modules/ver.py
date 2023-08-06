# This file is placed in the Public Domain.


from ..runtime import Cfg


## COMMANDS


def ver(event):
    event.reply(f"{Cfg.name.upper()} {Cfg.version}")
