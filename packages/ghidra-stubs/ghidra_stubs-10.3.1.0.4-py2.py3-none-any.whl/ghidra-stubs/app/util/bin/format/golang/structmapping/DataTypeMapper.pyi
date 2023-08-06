from typing import List
import ghidra.app.util.bin
import ghidra.app.util.bin.format.golang.structmapping
import ghidra.program.model.address
import ghidra.program.model.data
import ghidra.program.model.listing
import ghidra.util
import ghidra.util.task
import java.lang


class DataTypeMapper(object, java.lang.AutoCloseable):
    """
    Information about StructureMapping classes and their metadata, as well as
     accumulated information about structure instances that have been deserialized.
 
     To use the full might and majesty of StructureMapping(tm), a DataTypeMapper must be created. It
     must be able to #addArchiveSearchCategoryPath(CategoryPath...) 
     (#addProgramSearchCategoryPath(CategoryPath...)) the Ghidra structure data
     types being used, and it must #registerStructure(Class) about all classes that are
     going to participate during deserialization and markup.
 
     Structure mapped classes can receive a reference to the specific DataTypeMapper type that 
     created them by declaring a  field, and tagging it with 
     the @ContextField annotation:
 
 
     class MyDataTypeMapper extends DataTypeMapper {
      public MyDataTypeMapper() {
        ...
       registerStructure(MyDataType.class);
      }
      public void foo() { ... }
     }
 
     StructureMapping(structureName = "mydatatype")
     class MyDataType {
 
      ContextField
      private MyDataTypeMapper myDataTypeMapper;
  
      ContextField
      private StructureContextMyDataType context;
 
      FieldMapping
      private long someField;
 
     void bar() {
      context.getDataTypeMapper().getProgram(); // can only access methods defined on base DataTypeMapper type
      myDataTypeMapper.foo(); // same context as previous line, but typed correctly
     ...
 
    """









    def addArchiveSearchCategoryPath(self, paths: List[ghidra.program.model.data.CategoryPath]) -> ghidra.app.util.bin.format.golang.structmapping.DataTypeMapper: ...

    def addProgramSearchCategoryPath(self, paths: List[ghidra.program.model.data.CategoryPath]) -> ghidra.app.util.bin.format.golang.structmapping.DataTypeMapper: ...

    def close(self) -> None: ...

    def equals(self, __a0: object) -> bool: ...

    def getClass(self) -> java.lang.Class: ...

    def getCodeAddress(self, offset: long) -> ghidra.program.model.address.Address: ...

    def getDTM(self) -> ghidra.program.model.data.DataTypeManager: ...

    def getDataAddress(self, offset: long) -> ghidra.program.model.address.Address: ...

    def getDataConverter(self) -> ghidra.util.DataConverter: ...

    def getDefaultVariableLengthStructCategoryPath(self) -> ghidra.program.model.data.CategoryPath: ...

    def getExistingStructureAddress(self, structureInstance: object) -> ghidra.program.model.address.Address:
        """
        Attempts to convert an instance of an object (that represents a chunk of memory in
         the program) into its Address.
        @param <T> type of the object
        @param structureInstance instance of an object that represents something in the program's
         memory
        @return {@link Address} of the object, or null if not found or not a supported object
        @throws IOException
        """
        ...

    def getExistingStructureContext(self, structureInstance: object) -> ghidra.app.util.bin.format.golang.structmapping.StructureContext: ...

    def getProgram(self) -> ghidra.program.model.listing.Program: ...

    def getReader(self, position: long) -> ghidra.app.util.bin.BinaryReader: ...

    def getStructureDataType(self, clazz: java.lang.Class) -> ghidra.program.model.data.Structure:
        """
        Returns a Ghidra structure data type representing the specified class.
        @param clazz a structure mapped class
        @return {@link Structure} data type, or null if the class was a struct with variable length
         fields
        """
        ...

    def getStructureDataTypeName(self, clazz: java.lang.Class) -> unicode:
        """
        Returns the name of the Ghidra structure that has been registered for the specified
         structure mapped class.
        @param clazz
        @return 
        """
        ...

    @overload
    def getStructureMappingInfo(self, clazz: java.lang.Class) -> ghidra.app.util.bin.format.golang.structmapping.StructureMappingInfo: ...

    @overload
    def getStructureMappingInfo(self, structureInstance: object) -> ghidra.app.util.bin.format.golang.structmapping.StructureMappingInfo: ...

    def getType(self, name: unicode, clazz: java.lang.Class) -> object:
        """
        Returns a named {@link DataType}, searching the registered 
         {@link #addProgramSearchCategoryPath(CategoryPath...) program}
         and {@link #addArchiveSearchCategoryPath(CategoryPath...) archive} category paths.
        @param <T>
        @param name
        @param clazz
        @return 
        """
        ...

    def getTypeOrDefault(self, __a0: unicode, __a1: java.lang.Class, __a2: ghidra.program.model.data.DataType) -> ghidra.program.model.data.DataType: ...

    def hashCode(self) -> int: ...

    def labelAddress(self, addr: ghidra.program.model.address.Address, symbolName: unicode) -> None: ...

    def labelStructure(self, obj: object, symbolName: unicode) -> None: ...

    def markup(self, obj: object, nested: bool) -> None: ...

    @overload
    def markupAddress(self, addr: ghidra.program.model.address.Address, dt: ghidra.program.model.data.DataType) -> None: ...

    @overload
    def markupAddress(self, addr: ghidra.program.model.address.Address, dt: ghidra.program.model.data.DataType, length: int) -> None: ...

    def markupAddressIfUndefined(self, addr: ghidra.program.model.address.Address, dt: ghidra.program.model.data.DataType) -> None: ...

    def notify(self) -> None: ...

    def notifyAll(self) -> None: ...

    @overload
    def readStructure(self, structureClass: java.lang.Class, position: long) -> object: ...

    @overload
    def readStructure(self, structureClass: java.lang.Class, structReader: ghidra.app.util.bin.BinaryReader) -> object: ...

    @overload
    def readStructure(self, structureClass: java.lang.Class, address: ghidra.program.model.address.Address) -> object: ...

    def registerStructure(self, clazz: java.lang.Class) -> None:
        """
        Registers a class that has {@link StructureMapping structure mapping} information.
        @param <T>
        @param clazz
        @throws IOException if the class's Ghidra structure data type could not be found
        """
        ...

    def registerStructures(self, __a0: List[object]) -> None: ...

    def setMarkupTaskMonitor(self, monitor: ghidra.util.task.TaskMonitor) -> None: ...

    def toString(self) -> unicode: ...

    @overload
    def wait(self) -> None: ...

    @overload
    def wait(self, __a0: long) -> None: ...

    @overload
    def wait(self, __a0: long, __a1: int) -> None: ...

    @property
    def DTM(self) -> ghidra.program.model.data.DataTypeManager: ...

    @property
    def dataConverter(self) -> ghidra.util.DataConverter: ...

    @property
    def defaultVariableLengthStructCategoryPath(self) -> ghidra.program.model.data.CategoryPath: ...

    @property
    def markupTaskMonitor(self) -> None: ...  # No getter available.

    @markupTaskMonitor.setter
    def markupTaskMonitor(self, value: ghidra.util.task.TaskMonitor) -> None: ...

    @property
    def program(self) -> ghidra.program.model.listing.Program: ...