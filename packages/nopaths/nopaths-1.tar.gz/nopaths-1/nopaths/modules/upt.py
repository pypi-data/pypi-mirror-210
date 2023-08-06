# This file is placed in the Public Domain.


import time


from ..runtime import STARTTIME
from ..utility import elapsed


## COMMANDS


def upt(event):
    event.reply(elapsed(time.time()-STARTTIME))
