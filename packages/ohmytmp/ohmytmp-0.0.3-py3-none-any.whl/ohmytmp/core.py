import os
from copy import deepcopy as dcp

from .constant import FUNC, Info
from .plugin import *


class Ohmytmp:
    def __init__(self) -> None:
        self.func = {i: list() for i in FUNC.to_dict().values()}
        from .guesstype import guesstype
        self.register(PluginAnalysis(guesstype))

    def register(self, a: PluginBase,  lv: int = -1):
        try:
            b = a.TYPE
        except AttributeError:
            b = FUNC.AFTER
        if lv == -1:
            self.func[b].append(a)
            return
        if lv < 0:
            lv += 1
        self.func[b] = self.func[b][:lv] + [a,] + self.func[b][lv:]

    def init_file(self, p: str) -> Info:
        info = Info(p)
        for i in self.func[FUNC.ANALYSIS]:
            i.func(info)
        for i in self.func[FUNC.AFTER]:
            i.func(dcp(info))
        return info

    def walk(self, d: str):
        for p, _, f in os.walk(d):
            for i in f:
                self.init_file(os.path.join(p, i))
