import os
from typing import Callable

from .constant import Info, FUNC


class PluginBase:
    def __init__(self, func: Callable = None) -> None:
        self.TYPE = None
        if func is not None:
            self.func = func

    def func(self, *l, **d):
        pass


class PluginAnalysis(PluginBase):
    def __init__(self, func: Callable[[Info], None] = None) -> None:
        super().__init__(func)
        self.TYPE = FUNC.ANALYSIS

    # def func(self, info: Info) -> None:
    #     pass


class PluginAfter(PluginBase):
    def __init__(self, func: Callable[[Info], None] = None) -> None:
        super().__init__(func)
        self.TYPE = FUNC.AFTER

    # def func(self, _info: Info) -> None:
    #     pass
