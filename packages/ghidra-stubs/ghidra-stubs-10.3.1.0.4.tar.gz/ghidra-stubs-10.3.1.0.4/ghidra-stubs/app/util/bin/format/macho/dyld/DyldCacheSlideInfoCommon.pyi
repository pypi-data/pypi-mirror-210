import ghidra.app.util.bin
import ghidra.app.util.bin.format.macho.dyld
import ghidra.app.util.importer
import ghidra.program.model.data
import ghidra.program.model.listing
import ghidra.util.task
import java.lang


class DyldCacheSlideInfoCommon(object, ghidra.app.util.bin.StructConverter):
    """
    Class for representing the common components of the various dyld_cache_slide_info structures.
     The intent is for the the full dyld_cache_slide_info structures to extend this and add their
     specific parts.
    """

    ASCII: ghidra.program.model.data.DataType = char
    BYTE: ghidra.program.model.data.DataType = byte
    BYTES_PER_CHAIN_OFFSET: int = 4
    CHAIN_OFFSET_MASK: int = 16383
    DATA_PAGE_MAP_ENTRY: int = 1
    DWORD: ghidra.program.model.data.DataType = dword
    IBO32: ghidra.program.model.data.DataType = IBO32DataType: typedef ImageBaseOffset32 pointer32
    IBO64: ghidra.program.model.data.DataType = IBO64DataType: typedef ImageBaseOffset64 pointer64
    POINTER: ghidra.program.model.data.DataType = pointer
    QWORD: ghidra.program.model.data.DataType = qword
    SLEB128: ghidra.program.model.data.SignedLeb128DataType = sleb128
    STRING: ghidra.program.model.data.DataType = string
    ULEB128: ghidra.program.model.data.UnsignedLeb128DataType = uleb128
    UTF16: ghidra.program.model.data.DataType = unicode
    UTF8: ghidra.program.model.data.DataType = string-utf8
    VOID: ghidra.program.model.data.DataType = void
    WORD: ghidra.program.model.data.DataType = word



    def __init__(self, reader: ghidra.app.util.bin.BinaryReader):
        """
        Create a new {@link DyldCacheSlideInfoCommon}.
        @param reader A {@link BinaryReader} positioned at the start of a DYLD slide info
        @throws IOException if there was an IO-related problem creating the DYLD slide info
        """
        ...



    def equals(self, __a0: object) -> bool: ...

    def fixPageChains(self, program: ghidra.program.model.listing.Program, dyldCacheHeader: ghidra.app.util.bin.format.macho.dyld.DyldCacheHeader, addRelocations: bool, log: ghidra.app.util.importer.MessageLog, monitor: ghidra.util.task.TaskMonitor) -> None: ...

    def getClass(self) -> java.lang.Class: ...

    def getSlideInfoOffset(self) -> long:
        """
        Return the original slide info offset
        @return the original slide info offset
        """
        ...

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
    def slideInfoOffset(self) -> long: ...

    @property
    def version(self) -> int: ...