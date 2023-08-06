import ghidra.app.util.bin.format.macho
import ghidra.app.util.bin.format.macho.commands
import ghidra.app.util.importer
import ghidra.program.flatapi
import ghidra.program.model.address
import ghidra.program.model.data
import ghidra.program.model.listing
import ghidra.util.task
import java.lang


class FileSetEntryCommand(ghidra.app.util.bin.format.macho.commands.LoadCommand):
    """
    Represents a fileset_entry_command
    """









    def equals(self, __a0: object) -> bool: ...

    def getClass(self) -> java.lang.Class: ...

    def getCommandName(self) -> unicode: ...

    def getCommandSize(self) -> int:
        """
        Gets the size of this load command in bytes
        @return The size of this load command in bytes
        """
        ...

    def getCommandType(self) -> int:
        """
        Gets the type of this load command
        @return The type of this load command
        """
        ...

    def getFileOffset(self) -> long:
        """
        Gets the file offset of the DYLIB
        @return the file offset of the DYLIB
        """
        ...

    def getFileSetEntryId(self) -> ghidra.app.util.bin.format.macho.commands.LoadCommandString:
        """
        Gets the identifier of the DYLIB
        @return the identifier of the DYLIB
        """
        ...

    def getReserved(self) -> int:
        """
        Gets the reserved field (should just be padding)
        @return The reserved field
        """
        ...

    def getStartIndex(self) -> long:
        """
        Returns the binary start index of this load command
        @return the binary start index of this load command
        """
        ...

    def getVMaddress(self) -> long:
        """
        Gets the virtual address of the DYLIB
        @return The virtual address of the DYLIB
        """
        ...

    def hashCode(self) -> int: ...

    def markup(self, header: ghidra.app.util.bin.format.macho.MachHeader, api: ghidra.program.flatapi.FlatProgramAPI, baseAddress: ghidra.program.model.address.Address, isBinary: bool, parentModule: ghidra.program.model.listing.ProgramModule, monitor: ghidra.util.task.TaskMonitor, log: ghidra.app.util.importer.MessageLog) -> None: ...

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
    def VMaddress(self) -> long: ...

    @property
    def commandName(self) -> unicode: ...

    @property
    def fileOffset(self) -> long: ...

    @property
    def fileSetEntryId(self) -> ghidra.app.util.bin.format.macho.commands.LoadCommandString: ...

    @property
    def reserved(self) -> int: ...