import os


CONSTCHAR = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
CONSTCHAR0 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_'


def is_const(v: str) -> bool:
    return len(v) < 255 and v[0] in CONSTCHAR0 and all([i in CONSTCHAR for i in v[1:]])


class Const:
    def __init__(self) -> None:
        pass

    def to_dict(self) -> dict:
        ans = dict()
        for i in dir(self):
            if is_const(i):
                ans[i] = eval('self.%s' % i)
        return ans


class __func(Const):
    def __init__(self) -> None:
        super().__init__()
        self.ANALYSIS = 'analysis'
        self.AFTER = 'after'


FUNC = __func()


class __type(Const):
    def __init__(self) -> None:
        super().__init__()
        self.UNKNOWN = 'unknown'
        self.ARCHIVE = 'archive'
        self.VIDEO = 'video'
        self.AUDIO = 'audio'
        self.IMAGE = 'image'
        self.GIF = 'image/gif'
        self.SVG = 'image/svg'
        self.OFFICE = 'office'
        self.EXECUTABLE = 'executable'
        self.TEXT = 'text'
        self.CONFIG = 'text/config'
        self.CODE = 'text/code'


TYPE = __type()


class Info(Const):
    def __init__(self, src: str) -> None:
        super().__init__()
        self.SRC = os.path.abspath(os.path.expanduser(src))
        self.BASE = os.path.basename(self.SRC)
        self.EXT = os.path.splitext(self.BASE)[1][1:]
        self.TYPE = TYPE.UNKNOWN
        self.TAGS = list()

    def to_taglist(self, addlist: list = ['EXT', 'TYPE']) -> list:
        ans = self.TAGS.copy()
        d = self.to_dict()
        for i in addlist:
            if i in d and isinstance(d[i], str):
                ans.append('%s_%s' % (i, d[i]))
        return ans
