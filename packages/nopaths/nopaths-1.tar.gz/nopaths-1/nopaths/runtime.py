# This file is placed in the Pubic Domain.


import functools
import time


from .command import Commands
from .default import Default
from .errored import Errors
from .message import Message
from .objects import Object, kind, update
from .persist import Persist
from .threads import Thread
from .utility import fntime


def __dir__():
    return (
            'DATE',
            'STARTTIME',
            'Config',
            'Cfg',
            'command',
            'launch',
            'parse_cli',
            'threaded'
           ) 


DATE = time.ctime(time.time()).replace("  ", " ")
STARTTIME = time.time()


class Config(Default):

    pass


Cfg = Config()
Cfg.debug = False
Cfg.mod = "cmd,err,flt,mod,sts,thr,upt,ver"
Cfg.name = "nopaths"
Cfg.threaded = False
Cfg.version = "1"


def command(cli, txt) -> Message:
    evt = cli.event(txt)
    Commands.handle(evt)
    evt.ready()
    return evt


def launch(func, *args, **kwargs):
    thrname = kwargs.get('name', '')
    thr = Thread(func, thrname, *args)
    thr.start()
    return thr


def parse_cli(txt) -> Message:
    msg = Message()
    msg.parse(txt)
    update(Cfg, msg)
    Cfg.mod += msg.mods
    return Cfg


def threaded(func, *args, **kwargs):

    @functools.wraps(func)
    def threadedfunc(*args, **kwargs):
        thr = launch(func, *args, **kwargs)
        if args:
            args[0]._thr = thr
        return thr

    return threadedfunc
