# This file is placed in the Public Domain.


from .objects import Object


def __dir__():
    return (
            'Listens',
           )


class Listens(Object):

    objs = []

    @staticmethod
    def add(obj) -> None:
        Listens.objs.append(obj)

    @staticmethod
    def announce(txt) -> None:
        for obj in Listens.objs:
            obj.announce(txt)

    @staticmethod
    def byorig(orig) -> Object:
        for obj in Listens.objs:
            if repr(obj) == orig:
                return obj
        return None

    @staticmethod
    def remove(bot) -> None:
        try:
            Listens.objs.remove(bot)
        except ValueError:
            pass

    @staticmethod
    def say(orig, txt, channel=None) -> None:
        bot = Listens.byorig(orig)
        if bot:
            if channel:
                bot.say(channel, txt)
            else:
                bot.raw(txt)
