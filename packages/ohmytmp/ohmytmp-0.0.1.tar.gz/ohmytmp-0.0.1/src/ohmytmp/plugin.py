import os
from typing import Callable

from .constant import Info


class PluginBase:
    def __init__(self, _func: Callable = None) -> None:
        if _func is not None:
            self.update_func(_func)

    def update_func(self, _func: Callable) -> None:
        self._func = _func

    def func(self, *l, **d):
        return self._func(*l, **d)


class PluginGuessType(PluginBase):
    def __init__(self, _func: Callable[[str], str] = None) -> None:
        super().__init__(_func)

    # def _func(self, p: str) -> str:
    #     return TYPE.UNKNOWN


class PluginAnalysis(PluginBase):
    def __init__(self, _func: Callable[[Info], None] = None) -> None:
        super().__init__(_func)

    # def _func(self, info: Info) -> None:
    #     pass


class PluginDestination(PluginBase):
    def __init__(self, _func: Callable[[Info], str] = None) -> None:
        super().__init__(_func)
        self.flag = False

    def start(self) -> None:
        # mkdir
        self.flag = True

    # def _func(self, info: Info) -> str:
    #     return ''

    def mkdir(self, dst:str) -> None:
        if os.path.exists(dst):
            if not os.path.isdir(dst):
                raise FileExistsError(dst)
        else:
            os.makedirs(dst)

    def func(self, info: Info) -> str:
        if not self.flag:
            return ''
        return self._func(info)


class PluginAfter(PluginBase):
    def __init__(self, _func: Callable[[Info], None] = None) -> None:
        super().__init__(_func)

    # def _func(self, info: Info) -> None:
    #     pass
