from typing import List
import ghidra.app.util.bin
import ghidra.app.util.bin.format.macho.dyld
import ghidra.app.util.importer
import ghidra.program.model.data
import ghidra.program.model.listing
import ghidra.util.task
import java.lang


class DyldCacheSlideInfo1(ghidra.app.util.bin.format.macho.dyld.DyldCacheSlideInfoCommon):
    """
    Represents a dyld_cache_slide_info structure.
    """





    def __init__(self, reader: ghidra.app.util.bin.BinaryReader):
        """
        Create a new {@link DyldCacheSlideInfo1}.
        @param reader A {@link BinaryReader} positioned at the start of a DYLD slide info 1
        @throws IOException if there was an IO-related problem creating the DYLD slide info 1
        """
        ...



    def equals(self, __a0: object) -> bool: ...

    def fixPageChains(self, program: ghidra.program.model.listing.Program, dyldCacheHeader: ghidra.app.util.bin.format.macho.dyld.DyldCacheHeader, addRelocations: bool, log: ghidra.app.util.importer.MessageLog, monitor: ghidra.util.task.TaskMonitor) -> None: ...

    def getClass(self) -> java.lang.Class: ...

    def getEntries(self) -> List[int]: ...

    def getEntriesCount(self) -> int: ...

    def getEntriesOffset(self) -> int: ...

    def getEntriesSize(self) -> int: ...

    def getSlideInfoOffset(self) -> long:
        """
        Return the original slide info offset
        @return the original slide info offset
        """
        ...

    def getToc(self) -> List[int]: ...

    def getTocCount(self) -> int: ...

    def getTocOffset(self) -> int: ...

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
    def entries(self) -> List[int]: ...

    @property
    def entriesCount(self) -> int: ...

    @property
    def entriesOffset(self) -> int: ...

    @property
    def entriesSize(self) -> int: ...

    @property
    def toc(self) -> List[int]: ...

    @property
    def tocCount(self) -> int: ...

    @property
    def tocOffset(self) -> int: ...