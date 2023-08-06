# This file is placed in the Public Domain.


from ..listens import Listens
from ..objfunc import prt


## COMMANDS


def sts(event):
    for bot in Listens.objs:
        if 'state' in dir(bot):
            event.reply(prt(bot.state, skip='lastline'))
    else:
        event.reply("no status")
