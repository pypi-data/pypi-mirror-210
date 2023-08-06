import os

from ohmytmp import Info, PluginAfter


class DstOneDir(PluginAfter):
    def __init__(self, dst: str) -> None:
        self.data = dict()
        self.dst = os.path.abspath(os.path.expanduser(dst))
        super().__init__()
        self.flag = False

    def start(self) -> None:
        if not self.flag:
            self.mkdirs()
            self.flag = True

    def join(self, *paths) -> str:
        return os.path.abspath(os.path.join(self.dst, *paths))

    def mkdir(self, dst: str) -> None:
        if os.path.exists(dst):
            if not os.path.isdir(dst):
                raise FileExistsError(dst)
        else:
            os.makedirs(dst)

    def mkdirs(self) -> None:
        self.mkdir(self.dst)

    def get_dst(self, _info: Info) -> str:
        return self.dst

    def func(self, _info: Info) -> None:
        self.data[_info.SRC] = self.get_dst(_info)


class DstExtType(DstOneDir):
    def __init__(self, dst: str) -> None:
        super().__init__(dst)
        from ohmytmp import TYPE
        self.UNKNOWN = TYPE.UNKNOWN
        self.dsts = {i: self.join(self.dst, i)
                     for i in TYPE.to_dict().values()}

    def mkdirs(self) -> None:
        super().mkdirs()
        for i in self.dsts:
            self.mkdir(self.dsts[i])

    def get_dst(self, _info: Info) -> str:
        return self.dsts.get(_info.TYPE, self.dsts[self.UNKNOWN])
