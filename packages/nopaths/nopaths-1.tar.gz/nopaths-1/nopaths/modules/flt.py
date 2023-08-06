# This file is placed in the Public Domain.


from ..listens import Listens
from ..objects import kind
from ..objfunc import prt


## COMMANDS


def flt(event):
    try:
        index = int(event.args[0])
        event.reply(prt(Listens.objs[index]))
        return
    except (KeyError, TypeError, IndexError, ValueError):
        pass
    event.reply(' | '.join([kind(obj) for obj in Listens.objs]))
