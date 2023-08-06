from typing import List
import ghidra.app.util.bin
import ghidra.program.model.data
import java.lang


class DyldChainedStartsInSegment(object, ghidra.app.util.bin.StructConverter):
    """
    Represents a dyld_chained_starts_in_segment structure.
    """

    ASCII: ghidra.program.model.data.DataType = char
    BYTE: ghidra.program.model.data.DataType = byte
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







    def equals(self, __a0: object) -> bool: ...

    def getChain_starts(self) -> List[int]: ...

    def getClass(self) -> java.lang.Class: ...

    def getMaxValidPointer(self) -> int: ...

    def getPageCount(self) -> int: ...

    def getPageSize(self) -> int: ...

    def getPage_starts(self) -> List[int]: ...

    def getPointerFormat(self) -> int: ...

    def getSegmentOffset(self) -> long: ...

    def getSize(self) -> int: ...

    def hashCode(self) -> int: ...

    def notify(self) -> None: ...

    def notifyAll(self) -> None: ...

    def toDataType(self) -> ghidra.program.model.data.DataType: ...

    def toString(self) -> unicode: ...

    @overload
    def wait(self) -> None: ...

    @overload
    def wait(self, __a0: long) -> None: ...

    @overload
    def wait(self, __a0: long, __a1: int) -> None: ...

    @property
    def chain_starts(self) -> List[int]: ...

    @property
    def maxValidPointer(self) -> int: ...

    @property
    def pageCount(self) -> int: ...

    @property
    def pageSize(self) -> int: ...

    @property
    def page_starts(self) -> List[int]: ...

    @property
    def pointerFormat(self) -> int: ...

    @property
    def segmentOffset(self) -> long: ...

    @property
    def size(self) -> int: ...