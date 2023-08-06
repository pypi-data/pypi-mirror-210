from typing import List
import ghidra.app.util.bin
import ghidra.app.util.bin.format.macho.dyld
import ghidra.app.util.importer
import ghidra.program.model.data
import ghidra.program.model.listing
import ghidra.util.task
import java.lang


class DyldCacheSlideInfo4(ghidra.app.util.bin.format.macho.dyld.DyldCacheSlideInfoCommon):
    """
    Represents a dyld_cache_slide_info3 structure.
    """





    def __init__(self, reader: ghidra.app.util.bin.BinaryReader):
        """
        Create a new {@link DyldCacheSlideInfo3}.
        @param reader A {@link BinaryReader} positioned at the start of a DYLD slide info 3
        @throws IOException if there was an IO-related problem creating the DYLD slide info 3
        """
        ...



    def equals(self, __a0: object) -> bool: ...

    def fixPageChains(self, program: ghidra.program.model.listing.Program, dyldCacheHeader: ghidra.app.util.bin.format.macho.dyld.DyldCacheHeader, addRelocations: bool, log: ghidra.app.util.importer.MessageLog, monitor: ghidra.util.task.TaskMonitor) -> None: ...

    def getClass(self) -> java.lang.Class: ...

    def getDeltaMask(self) -> long: ...

    def getPageExtras(self) -> List[int]: ...

    def getPageExtrasCount(self) -> int: ...

    def getPageExtrasOffset(self) -> int: ...

    def getPageSize(self) -> int: ...

    def getPageStarts(self) -> List[int]: ...

    def getPageStartsCount(self) -> int: ...

    def getPageStartsOffset(self) -> int: ...

    def getSlideInfoOffset(self) -> long:
        """
        Return the original slide info offset
        @return the original slide info offset
        """
        ...

    def getValueAdd(self) -> long: ...

    def getVersion(self) -> int:
        """
        Gets the version of the DYLD slide info.
        @return The version of the DYLD slide info.
        """
        ...

    def hashCode(self) -> int: ...

    def notify(self) -> None: ...

    def notifyAll(self) -> None: ...

    @staticmethod
    def parseSlideInfo(reader: ghidra.app.util.bin.BinaryReader, slideInfoOffset: long, log: ghidra.app.util.importer.MessageLog, monitor: ghidra.util.task.TaskMonitor) -> ghidra.app.util.bin.format.macho.dyld.DyldCacheSlideInfoCommon:
        """
        Parses the slide info
        @param reader A {@link BinaryReader} positioned at the start of a DYLD slide info
        @param slideInfoOffset The offset of the slide info to parse
        @param log The log
        @param monitor A cancelable task monitor
        @return The slide info object
        """
        ...

    def toDataType(self) -> ghidra.program.model.data.DataType: ...

    def toString(self) -> unicode: ...

    @overload
    def wait(self) -> None: ...

    @overload
    def wait(self, __a0: long) -> None: ...

    @overload
    def wait(self, __a0: long, __a1: int) -> None: ...

    @property
    def deltaMask(self) -> long: ...

    @property
    def pageExtras(self) -> List[int]: ...

    @property
    def pageExtrasCount(self) -> int: ...

    @property
    def pageExtrasOffset(self) -> int: ...

    @property
    def pageSize(self) -> int: ...

    @property
    def pageStarts(self) -> List[int]: ...

    @property
    def pageStartsCount(self) -> int: ...

    @property
    def pageStartsOffset(self) -> int: ...

    @property
    def valueAdd(self) -> long: ...