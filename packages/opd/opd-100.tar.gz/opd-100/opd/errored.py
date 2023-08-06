# This file is placed in the Public Domain.


from .objects import  Object


class Error(Exception):

    pass


class NoClassError(Error):

    pass


class Errors(Object):

    errors = []

    @staticmethod
    def handle(ex):
        exc = ex.with_traceback(ex.__traceback__)
        Errors.errors.append(exc)
