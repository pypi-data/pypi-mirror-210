import os
from copy import deepcopy as dcp

from .guesstype import get_ext
from .constant import FUNC, TYPE, Info
from .plugin import *


class Initializer:
    def __init__(self, defaultdst: str) -> None:
        self.func = {i: list() for i in FUNC.to_dict().values()}

        from .guesstype import guess_ext, guess_mime
        self.reg_guesstype(PluginGuessType(guess_ext))
        self.reg_guesstype(PluginGuessType(guess_mime))
        self.reg_analysis(PluginAnalysis(self.__analysis))
        from .destination import DstExtType
        self.reg_destination(DstExtType(defaultdst))

    def register(self, a: PluginBase, b: str, lv: int = -1):
        if lv == -1:
            self.func[b].append(a)
            return
        if lv < 0:
            lv += 1
        self.func[b] = self.func[b][:lv] + [a,] + self.func[b][lv:]

    def reg_guesstype(self, a: PluginGuessType, lv: int = -1):
        self.register(a, FUNC.GUESSTYPE, lv)

    def reg_analysis(self, a: PluginAnalysis):
        self.register(a, FUNC.ANALYSIS)

    def reg_destination(self, a: PluginDestination, lv: int = -1):
        self.register(a, FUNC.DESTINATION, lv)

    def reg_after(self, a: PluginAfter):
        self.register(a, FUNC.AFTER)

    def exec_guesstype(self, p: str) -> str:
        for i in self.func[FUNC.GUESSTYPE]:
            ans = i.func(p)
            if ans != TYPE.UNKNOWN:
                return ans
        return ans

    def exec_analysis(self, info: Info) -> None:
        for i in self.func[FUNC.ANALYSIS]:
            i.func(info)

    def exec_destination(self, info: Info) -> None:
        for i in self.func[FUNC.DESTINATION][::-1]:
            ans = i.func(info)
            if ans is not None:
                return ans
        raise ValueError(info.to_dict())

    def exec_after(self, info: Info) -> None:
        for i in self.func[FUNC.AFTER]:
            i.func(dcp(info))

    def __analysis(self, info: Info) -> None:
        e = get_ext(info.SRC)
        info.EXT = e
        info.TYPE = self.exec_guesstype(info.SRC)

    def init_file(self, p: str) -> Info:
        info = Info(p)
        self.exec_analysis(info)
        info.DST = self.exec_destination(info)
        return info

    def walk(self, d: str):
        for p, _, f in os.walk(d):
            for i in f:
                self.init_file(os.path.join(p, i))
