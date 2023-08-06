import ghidra.app.util.bin
import ghidra.app.util.bin.format.golang.structmapping
import ghidra.program.model.address
import ghidra.program.model.data
import ghidra.program.model.listing
import java.lang


class StructureContext(object):
    """
    Information about an instance of a structure that has been read from the memory of a 
     Ghidra program.
 
     All StructureMapping tagged classes must have a ContextField tagged
     StructureContext field for that class to be able to access meta-data about its self, and
     for other classes to reference it when performing markup:
 
     StructureMapping(structureName = "mydatatype")
     class MyDataType {
     	ContextField
     	private StructureContextMyDataType context;
 
     	FieldMapping
     	private long someField;
      ...
 
    """





    def __init__(self, dataTypeMapper: ghidra.app.util.bin.format.golang.structmapping.DataTypeMapper, mappingInfo: ghidra.app.util.bin.format.golang.structmapping.StructureMappingInfo, reader: ghidra.app.util.bin.BinaryReader): ...



    def appendComment(self, commentType: int, prefix: unicode, comment: unicode, sep: unicode) -> None:
        """
        Places a comment at the start of this structure, appending to any previous values 
         already there.
        @param commentType
        @param prefix
        @param comment
        @param sep
        @throws IOException
        """
        ...

    def createFieldContext(self, fmi: ghidra.app.util.bin.format.golang.structmapping.FieldMappingInfo, includeReader: bool) -> ghidra.app.util.bin.format.golang.structmapping.FieldContext: ...

    def equals(self, __a0: object) -> bool: ...

    def getClass(self) -> java.lang.Class: ...

    def getDataTypeMapper(self) -> ghidra.app.util.bin.format.golang.structmapping.DataTypeMapper:
        """
        Returns a reference to the root {@link DataTypeMapper}, as a plain DataTypeMapper type.  If
         a more specific DataTypeMapper type is needed, either type-cast this value, or use
         a {@link ContextField} tag on a field in your class that specifies the correct 
         DataTypeMapper type.
        @return 
        """
        ...

    def getFieldAddress(self, fieldOffset: long) -> ghidra.program.model.address.Address:
        """
        Returns the address of an offset from the start of this structure instance.
        @param fieldOffset
        @return 
        """
        ...

    def getFieldLocation(self, fieldOffset: long) -> long:
        """
        Returns the stream location of an offset from the start of this structure instance.
        @param fieldOffset
        @return 
        """
        ...

    def getFieldReader(self, fieldOffset: long) -> ghidra.app.util.bin.BinaryReader:
        """
        Returns an independent {@link BinaryReader} that is positioned at the start of the
         specified field.
        @param fieldOffset
        @return 
        """
        ...

    def getMappingInfo(self) -> ghidra.app.util.bin.format.golang.structmapping.StructureMappingInfo:
        """
        Returns the {@link StructureMappingInfo} for this structure's class.
        @return 
        """
        ...

    def getProgram(self) -> ghidra.program.model.listing.Program: ...

    def getReader(self) -> ghidra.app.util.bin.BinaryReader: ...

    def getStructureAddress(self) -> ghidra.program.model.address.Address:
        """
        Returns the address in the program of this structure instance.
        @return {@link Address}
        """
        ...

    def getStructureDataType(self) -> ghidra.program.model.data.Structure: ...

    def getStructureEnd(self) -> long:
        """
        Returns the stream location of the end of this structure instance.
        @return 
        """
        ...

    def getStructureInstance(self) -> object: ...

    def getStructureLength(self) -> int:
        """
        Returns the length of this structure instance.
        @return 
        """
        ...

    def getStructureStart(self) -> long:
        """
        Returns the stream location of this structure instance.
        @return 
        """
        ...

    def hashCode(self) -> int: ...

    def isAlreadyMarkedup(self) -> bool: ...

    def markupFields(self) -> None: ...

    def markupStructure(self, nested: bool) -> None:
        """
        @param nested if true, it is assumed that the Ghidra data types have already been
         placed and only markup needs to be performed.
        @throws IOException
        """
        ...

    def notify(self) -> None: ...

    def notifyAll(self) -> None: ...

    def readNewInstance(self) -> object: ...

    def toString(self) -> unicode: ...

    @overload
    def wait(self) -> None: ...

    @overload
    def wait(self, __a0: long) -> None: ...

    @overload
    def wait(self, __a0: long, __a1: int) -> None: ...

    @property
    def alreadyMarkedup(self) -> bool: ...

    @property
    def dataTypeMapper(self) -> ghidra.app.util.bin.format.golang.structmapping.DataTypeMapper: ...

    @property
    def mappingInfo(self) -> ghidra.app.util.bin.format.golang.structmapping.StructureMappingInfo: ...

    @property
    def program(self) -> ghidra.program.model.listing.Program: ...

    @property
    def reader(self) -> ghidra.app.util.bin.BinaryReader: ...

    @property
    def structureAddress(self) -> ghidra.program.model.address.Address: ...

    @property
    def structureDataType(self) -> ghidra.program.model.data.Structure: ...

    @property
    def structureEnd(self) -> long: ...

    @property
    def structureInstance(self) -> object: ...

    @property
    def structureLength(self) -> int: ...

    @property
    def structureStart(self) -> long: ...