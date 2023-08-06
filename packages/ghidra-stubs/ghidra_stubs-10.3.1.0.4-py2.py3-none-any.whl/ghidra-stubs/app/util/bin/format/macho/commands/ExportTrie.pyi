from typing import List
import ghidra.app.util.bin.format.macho.commands.ExportTrie
import java.lang
import java.util.function


class ExportTrie(object):
    """
    Mach-O export trie
    """






    class ExportEntry(object):




        def __init__(self, __a0: unicode, __a1: long, __a2: long, __a3: long, __a4: unicode): ...



        def equals(self, __a0: object) -> bool: ...

        def getAddress(self) -> long: ...

        def getClass(self) -> java.lang.Class: ...

        def getFlags(self) -> long: ...

        def getImportName(self) -> unicode: ...

        def getName(self) -> unicode: ...

        def getOther(self) -> long: ...

        def hashCode(self) -> int: ...

        def isReExport(self) -> bool: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @property
        def address(self) -> long: ...

        @property
        def flags(self) -> long: ...

        @property
        def importName(self) -> unicode: ...

        @property
        def name(self) -> unicode: ...

        @property
        def other(self) -> long: ...

        @property
        def reExport(self) -> bool: ...

    @overload
    def __init__(self):
        """
        Creates an empty {@link ExportTrie}.  This is useful for export trie load commands that are
         defined but do not point to any data.
        """
        ...

    @overload
    def __init__(self, reader: ghidra.app.util.bin.BinaryReader):
        """
        Creates and parses a new {@link ExportTrie}
        @param reader A {@link BinaryReader reader} positioned at the start of the export trie
        @throws IOException if an IO-related error occurs while parsing
        """
        ...



    def equals(self, __a0: object) -> bool: ...

    def getClass(self) -> java.lang.Class: ...

    @overload
    def getExports(self) -> List[ghidra.app.util.bin.format.macho.commands.ExportTrie.ExportEntry]:
        """
        Gets the {@link List} of {@link ExportEntry exports}
        @return The {@link List} of {@link ExportEntry exports}
        """
        ...

    @overload
    def getExports(self, filter: java.util.function.Predicate) -> List[ghidra.app.util.bin.format.macho.commands.ExportTrie.ExportEntry]:
        """
        Gets the {@link List} of {@link ExportEntry exports}
        @param filter A filter on the returned {@link List}
        @return The {@link List} of {@link ExportEntry exports}
        """
        ...

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

    @property
    def exports(self) -> List[object]: ...