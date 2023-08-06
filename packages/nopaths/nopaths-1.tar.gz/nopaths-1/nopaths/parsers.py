# This file is placed in the Public Domain.


from .default import Default
from .utility import spl


def __dir__():
    return (
            'parse',
           )


def parse(obj, txt):
    obj.otxt = txt
    splitted = obj.otxt.split()
    args = []
    _nr = -1
    for word in splitted:
        if word.startswith('-'):
            if not obj.index:
                obj.index = 0
            try:
                obj.index = int(word[1:])
            except ValueError:
                if not obj.opts:
                    obj.opts = ""
                obj.opts = obj.opts + word[1:]
            continue
        try:
            key, value = word.split('==')
            if not obj.skip:
                obj.skip = Default()
            if value.endswith('-'):
                value = value[:-1]
                setattr(obj.skip, value, '')
            if not obj.gets:
                obj.gets = Default()
            setattr(obj.gets, key, value)
            continue
        except ValueError:
            pass
        try:
            key, value = word.split('=')
            if key == "mod":
                if not obj.mod:
                    obj.mod = ""
                for val in spl(value):
                    if val not in obj.mods:
                        obj.mods += f",{val}"
                continue
            if not obj.sets:
                obj.sets = Default()
            setattr(obj.sets, key, value)
            continue
        except ValueError:
            pass
        _nr += 1
        if _nr == 0:
            obj.cmd = word
            continue
        args.append(word)
    if args:
        obj.args = args
        obj.rest = ' '.join(args)
        obj.txt = obj.cmd + ' ' + obj.rest
    else:
        obj.txt = obj.cmd
