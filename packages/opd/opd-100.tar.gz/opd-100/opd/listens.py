# This file is placed in the Public Domain.


from .objects import Object


class Listens(Object):

    objs = []

    @staticmethod
    def add(obj):
        Listens.objs.append(obj)

    @staticmethod
    def announce(txt):
        for obj in Listens.objs:
            obj.announce(txt)

    @staticmethod
    def byorig(orig):
        for obj in Listens.objs:
            if repr(obj) == orig:
                return obj
        return None

    @staticmethod
    def remove(bot):
        try:
            Listens.objs.remove(bot)
        except ValueError:
            pass

    @staticmethod
    def say(orig, txt, channel=None):
        bot = Listens.byorig(orig)
        if bot:
            if channel:
                bot.say(channel, txt)
            else:
                bot.raw(txt)
