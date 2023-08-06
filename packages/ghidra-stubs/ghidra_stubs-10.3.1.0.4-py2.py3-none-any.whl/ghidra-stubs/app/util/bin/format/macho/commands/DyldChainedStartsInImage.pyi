from typing import List
import ghidra.app.util.bin
import ghidra.app.util.bin.format.macho.commands
import ghidra.program.model.data
import java.lang


class DyldChainedStartsInImage(object, ghidra.app.util.bin.StructConverter):
    """
    Represents a dyld_chained_starts_in_image structure.
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

    def getChainedStarts(self) -> List[ghidra.app.util.bin.format.macho.commands.DyldChainedStartsInSegment]: ...

    def getClass(self) -> java.lang.Class: ...

    def getSeg_count(self) -> int: ...

    def getSeg_info_offset(self) -> List[int]: ...

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
    def chainedStarts(self) -> List[ghidra.app.util.bin.format.macho.commands.DyldChainedStartsInSegment]: ...

    @property
    def seg_count(self) -> int: ...

    @property
    def seg_info_offset(self) -> List[int]: ...