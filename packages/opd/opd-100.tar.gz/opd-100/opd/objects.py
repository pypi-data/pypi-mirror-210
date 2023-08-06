# This file is placed in the Public Domain.


import datetime
import os
import uuid


def __dir__():
    return (
            'Object',
            'edit',
            'items',
            'keys',
            'kind',
            'prt',
            'search',
            'update',
            'values',
           )


__all__ = __dir__()


class Object:

    __slots__ = ('__dict__', '__oid__')

    def __init__(self, *args, **kwargs):
        self.__oid__ = ident(self)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


def copy(obj, val):
    if isinstance(val, list):
        update(obj, dict(val))
    elif isinstance(val, zip):
        update(obj, dict(val))
    elif isinstance(val, dict):
        update(obj, val)
    elif isinstance(val, Object):
        update(obj, vars(val))


def edit(obj, setter, skip=False):
    try:
        setter = vars(setter)
    except (TypeError, ValueError):
        pass
    if not setter:
        setter = {}
    count = 0
    for key, val in setter.items():
        if skip and val == "":
            continue
        count += 1
        try:
            setattr(obj, key, int(val))
            continue
        except ValueError:
            pass
        try:
            setattr(obj, key, float(val))
            continue
        except ValueError:
            pass
        if val in ["True", "true"]:
            setattr(obj, key, True)
        elif val in ["False", "false"]:
            setattr(obj, key, False)
        else:
            setattr(obj, key, val)
    return count


def ident(obj):
    return os.path.join(
                        kind(obj),
                        str(uuid.uuid4().hex),
                        os.sep.join(str(datetime.datetime.now()).split())
                       )


def items(obj) -> []:
    if isinstance(obj, type({})):
        return obj.items()
    return obj.__dict__.items()


def keys(obj) -> []:
    return obj.__dict__.keys()


def kind(obj) -> str:
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = obj.__name__
    return kin


def prt(obj, args="", skip="", plain=False):
    res = []
    keyz = []
    if "," in args:
        keyz = args.split(",")
    if not keyz:
        keyz = keys(obj)
    for key in sorted(keyz):
        if key.startswith("_"):
            continue
        if skip:
            skips = skip.split(",")
            if key in skips:
                continue
        value = getattr(obj, key, None)
        if not value:
            continue
        if " object at " in str(value):
            continue
        txt = ""
        if plain:
            value = str(value)
            txt = f'{value}'
        elif isinstance(value, str) and len(value.split()) >= 2:
            txt = f'{key}="{value}"'
        else:
            txt = f'{key}={value}'
        res.append(txt)
    txt = " ".join(res)
    return txt.strip()


def search(obj, selector) -> bool:
    res = False
    select = Object(selector)
    for key, value in items(select):
        try:
            val = getattr(obj, key)
        except AttributeError:
            continue
        if str(value) in str(val):
            res = True
            break
    return res


def update(obj, data, empty=True) -> None:
    for key, value in items(data):
        if not empty and not value:
            continue
        setattr(obj, key, value)


def values(obj) -> []:
    return obj.__dict__.values()
