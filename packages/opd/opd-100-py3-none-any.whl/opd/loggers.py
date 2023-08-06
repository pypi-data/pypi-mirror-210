# This file is placed in the Public Domain.


from .utility import doskip, spl


SKIP = "PING,PONG"


class Logging:

    verbose = False

    @staticmethod
    def debug(txt):
        if Logging.verbose and not doskip(txt, SKIP):
            Logging.raw(txt)

    @staticmethod
    def raw(txt):
        pass
