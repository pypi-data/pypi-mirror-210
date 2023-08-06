# This file is placed in the Public Domain.


import time


from ..objects import Object
from ..persist import Persist, write
from ..utility import elapsed, fntime


class Log(Object):

    def __init__(self):
        super().__init__()
        self.txt = ''


Persist.add(Log)


## COMMANDS


def log(event):
    if not event.rest:
        nmr = 0
        for obj in Persist.find('log'):
            lap = elapsed(time.time() - fntime(obj.__oid__))
            event.reply(f'{nmr} {obj.txt} {lap}')
            nmr += 1
        if not nmr:
            event.reply('no log')
        return
    obj = Log()
    obj.txt = event.rest
    write(obj)
    event.reply('ok')
