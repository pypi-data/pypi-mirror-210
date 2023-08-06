import ghidra.app.util.bin
import ghidra.app.util.opinion
import ghidra.formats.gfilesystem
import ghidra.util.task
import java.lang


class DyldCacheDylibExtractor(object):




    def __init__(self): ...



    def equals(self, __a0: object) -> bool: ...

    @staticmethod
    def extractDylib(__a0: long, __a1: ghidra.app.util.opinion.DyldCacheUtils.SplitDyldCache, __a2: int, __a3: ghidra.formats.gfilesystem.FSRL, __a4: ghidra.util.task.TaskMonitor) -> ghidra.app.util.bin.ByteProvider: ...

    def getClass(self) -> java.lang.Class: ...

    def hashCode(self) -> int: ...

    def notify(self) -> None: ...

    def notifyAll(self) -> None: ...

    def toString(self) -> unicode: ...

    @overload
    def wait(self) -> None: ...

    @overload
    def wait(self, __a0: long) -> None: ...

    @overload
    def wait(self, __a0: long, __a1: int) -> None: ...

