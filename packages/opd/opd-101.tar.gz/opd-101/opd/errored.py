# This file is placed in the Public Domain.


from .objects import  Object


def __dir__():
    return (
            'Error',
            'Errors'
           )


class Error(Exception):

    pass


class Errors(Object):

    errors = []

    @staticmethod
    def handle(ex) -> None:
        exc = ex.with_traceback(ex.__traceback__)
        Errors.errors.append(exc)
