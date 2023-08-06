import os

from .constant import Info, TYPE
from .plugin import PluginDestination


class DstOneDir(PluginDestination):
    def __init__(self, dst: str) -> None:
        self.__dst = os.path.abspath(os.path.expanduser(dst))

        def __func(info: Info) -> str:
            return self.__dst
        super().__init__(__func)
        self.start()

    def start(self) -> None:
        self.mkdir(self.__dst)
        self.flag = True


class DstExtType(PluginDestination):
    def __init__(self, dst: str) -> None:
        self.__dst = os.path.abspath(os.path.expanduser(dst))
        self.data = {i: os.path.abspath(os.path.join(self.__dst, i))
            for i in TYPE.to_dict().values()}
        print(self.data)

        def __func(info: Info) -> str:
            return self.data.get(info.TYPE, self.data[TYPE.UNKNOWN])
        super().__init__(__func)
        self.start()

    def start(self) -> None:
        self.mkdir(self.__dst)
        for i in self.data:
            self.mkdir(self.data[i])
        self.flag = True
