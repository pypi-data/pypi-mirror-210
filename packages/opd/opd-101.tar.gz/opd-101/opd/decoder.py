# This file is placed in the Public Domain.


import json


from .objects import Object, copy


def __dir__():
    return (
            'ObjectDecoder',
            'load',
            'loads'
           )


class ObjectDecoder(json.JSONDecoder):

    def decode(self, s, _w=None) -> Object:
        val = json.JSONDecoder.decode(self, s)
        if not val:
            val = {}
        obj = Object()
        copy(obj, val)
        return obj

    def raw_decode(self, s, idx=0) -> (int, Object):
        return json.JSONDecoder.raw_decode(self, s, idx)


def load(fpt, *args, **kw) -> Object:
    return json.load(fpt, *args, cls=ObjectDecoder, **kw)


def loads(string, *args, **kw) -> Object:
    return json.loads(string, *args, cls=ObjectDecoder, **kw)
