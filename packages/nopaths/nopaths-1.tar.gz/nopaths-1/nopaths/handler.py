# This file is placed in the Public Domain.


import queue
import ssl
import threading


from .errored import Errors
from .objects import Object
from .message import Message
from .runtime import Cfg, launch


def __dir__():
    return (
            'Handler',
           )


class Handler(Object):

    def __init__(self):
        Object.__init__(self)
        self.cbs = Object()
        self.queue = queue.Queue()
        self.stopped = threading.Event()
        self.threaded = True

    def event(self, txt) -> Message:
        msg = Message()
        msg.type = 'command'
        msg.orig = repr(self)
        msg.parse(txt)
        return msg

    def handle(self, evt) -> Message:
        func = getattr(self.cbs, evt.type, None)
        if func:
            if "t" in Cfg.opts:
                evt._thr = launch(dispatch, func, evt, name=evt.cmd)
            else:
                dispatch(func, evt)
        return evt

    def loop(self) -> None:
        while not self.stopped.is_set():
            try:
                self.handle(self.poll())
            except (ssl.SSLError, EOFError, KeyboardInterrupt) as ex:
                Errors.handle(ex)
                self.restart()

    def one(self, txt) -> Message:
        return self.handle(self.event(txt))

    def poll(self) -> Message:
        return self.queue.get()

    def put(self, evt) -> None:
        self.queue.put_nowait(evt)

    def register(self, cmd, func) -> None:
        setattr(self.cbs, cmd, func)

    def restart(self) -> None:
        self.stop()
        self.start()

    def start(self) -> None:
        launch(self.loop)

    def stop(self) -> None:
        self.stopped.set()
        self.queue.put_nowait(None)


## HANDLERS


def dispatch(func, evt) -> None:
    try:
        func(evt)
    except Exception as ex:
        exc = ex.with_traceback(ex.__traceback__)
        Errors.errors.append(exc)
        evt.ready()
