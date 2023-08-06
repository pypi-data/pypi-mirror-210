# This file is placed in the Public Domain.


import time


from ..objects import Object
from ..persist import Persist, write
from ..utility import elapsed, fntime


class Todo(Object):

    def __init__(self):
        super().__init__()
        self.txt = ''


Persist.add(Todo)


## COMMANDS


def dne(event):
    if not event.args:
        return
    selector = {'txt': event.args[0]}
    for obj in Persist.find('todo', selector):
        obj.__deleted__ = True
        write(obj)
        event.reply('ok')
        break


def tdo(event):
    if not event.rest:
        nr = 0
        for obj in Persist.find('todo'):
            lap = elapsed(time.time()-fntime(obj.__oid__))
            event.reply(f'{nr} {obj.txt} {lap}')
            nr += 1
        if not nr:
            event.reply("no todo")
        return
    o = Todo()
    o.txt = event.rest
    write(o)
    event.reply('ok')
