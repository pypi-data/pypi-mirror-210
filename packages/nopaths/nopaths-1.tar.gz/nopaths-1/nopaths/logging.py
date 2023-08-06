# This file is placed in the Public Domain.


from .runtime import Cfg
from .utility import doskip, spl


def __dir__():
    return (
            'Logging',
           )


class Logging:

    verbose = False

    @staticmethod
    def debug(txt) -> None:
        if Logging.verbose and not doskip(txt, Cfg.skip):
            Logging.raw(txt)

    @staticmethod
    def raw(txt) -> None:
        pass
