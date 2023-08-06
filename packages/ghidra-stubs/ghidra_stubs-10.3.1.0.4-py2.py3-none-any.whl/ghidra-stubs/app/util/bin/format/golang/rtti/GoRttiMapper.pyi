from typing import List
import generic.jar
import ghidra.app.util.bin
import ghidra.app.util.bin.format.golang
import ghidra.app.util.bin.format.golang.rtti
import ghidra.app.util.bin.format.golang.rtti.types
import ghidra.app.util.bin.format.golang.structmapping
import ghidra.app.util.importer
import ghidra.program.model.address
import ghidra.program.model.data
import ghidra.program.model.listing
import ghidra.util
import ghidra.util.task
import java.io
import java.lang


class GoRttiMapper(ghidra.app.util.bin.format.golang.structmapping.DataTypeMapper):
    """
    DataTypeMapper for golang binaries. 
 
     When bootstrapping golang binaries, the following steps are used:
 
     	Find the GoBuildInfo struct.  This struct is the easiest to locate, even when the binary
     	is stripped.  This gives us the go pointerSize (probably same as ghidra pointer size) and the
     	goVersion.  This struct does not rely on StructureMapping, allowing its use before a
     	DataTypeMapper is created.
     	Create DataTypeMapper
     	Find the runtime.firstmoduledata structure.
 		
    			If there are symbols, just use the symbol or named memory block.
    			If stripped:
				
     					Find the pclntab.  This has a magic signature, a pointerSize, and references
     					to a couple of tables that are also referenced in the moduledata structure.
     					Search memory for a pointer to the pclntab struct.  This should be the first
     					field of the moduledata structure.  The values that are duplicated between the
     					two structures can be compared to ensure validity.
     					Different binary formats (Elf vs PE) will determine which memory blocks to
     					search.
 				  
 		
 
    """





    def __init__(self, program: ghidra.program.model.listing.Program, ptrSize: int, endian: ghidra.program.model.lang.Endian, goVersion: ghidra.app.util.bin.format.golang.GoVer, archiveGDT: generic.jar.ResourceFile): ...



    def addArchiveSearchCategoryPath(self, paths: List[ghidra.program.model.data.CategoryPath]) -> ghidra.app.util.bin.format.golang.structmapping.DataTypeMapper: ...

    def addModule(self, module: ghidra.app.util.bin.format.golang.rtti.GoModuledata) -> None: ...

    def addProgramSearchCategoryPath(self, paths: List[ghidra.program.model.data.CategoryPath]) -> ghidra.app.util.bin.format.golang.structmapping.DataTypeMapper: ...

    def cacheRecoveredDataType(self, typ: ghidra.app.util.bin.format.golang.rtti.types.GoType, dt: ghidra.program.model.data.DataType) -> None: ...

    def close(self) -> None: ...

    def discoverGoTypes(self, monitor: ghidra.util.task.TaskMonitor) -> None: ...

    def equals(self, __a0: object) -> bool: ...

    def exportTypesToGDT(self, gdtFile: java.io.File, monitor: ghidra.util.task.TaskMonitor) -> None:
        """
        Export the currently registered struct mapping types to a gdt file.
         <p>
         The struct data types will either be from the current program's DWARF data, or
         from an earlier golang.gdt (if this binary doesn't have DWARF)
        @param gdtFile
        @throws IOException
        """
        ...

    def findContainingModule(self, offset: long) -> ghidra.app.util.bin.format.golang.rtti.GoModuledata: ...

    def findContainingModuleByFuncData(self, offset: long) -> ghidra.app.util.bin.format.golang.rtti.GoModuledata: ...

    def findGoType(self, typeName: unicode) -> ghidra.app.util.bin.format.golang.rtti.types.GoType: ...

    @staticmethod
    def findGolangBootstrapGDT(goVer: ghidra.app.util.bin.format.golang.GoVer, ptrSize: int, osName: unicode) -> generic.jar.ResourceFile:
        """
        Searches for a golang bootstrap gdt file that matches the specified Go version/size/OS.
         <p>
         First looks for a gdt with an exact match, then for a gdt with version/size match and
         "any" OS, and finally, a gdt that matches the version and "any" size and "any" OS.
        @param goVer version of Go
        @param ptrSize size of pointers
        @param osName name of OS
        @return 
        """
        ...

    def getCachedRecoveredDataType(self, typ: ghidra.app.util.bin.format.golang.rtti.types.GoType) -> ghidra.program.model.data.DataType: ...

    def getChanGoType(self) -> ghidra.app.util.bin.format.golang.rtti.types.GoType: ...

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

    def getFirstModule(self) -> ghidra.app.util.bin.format.golang.rtti.GoModuledata: ...

    @staticmethod
    def getGDTFilename(goVer: ghidra.app.util.bin.format.golang.GoVer, pointerSizeInBytes: int, osName: unicode) -> unicode: ...

    def getGenericSliceDT(self) -> ghidra.program.model.data.Structure: ...

    def getGhidraDataType(self, goTypeName: unicode, clazz: java.lang.Class) -> object: ...

    def getGoName(self, offset: long) -> ghidra.app.util.bin.format.golang.rtti.GoName: ...

    @overload
    def getGoType(self, offset: long) -> ghidra.app.util.bin.format.golang.rtti.types.GoType: ...

    @overload
    def getGoType(self, addr: ghidra.program.model.address.Address) -> ghidra.app.util.bin.format.golang.rtti.types.GoType: ...

    @staticmethod
    def getGolangOSString(program: ghidra.program.model.listing.Program) -> unicode: ...

    def getGolangVersion(self) -> ghidra.app.util.bin.format.golang.GoVer: ...

    def getInt32DT(self) -> ghidra.program.model.data.DataType: ...

    def getMapGoType(self) -> ghidra.app.util.bin.format.golang.rtti.types.GoType: ...

    @staticmethod
    def getMapperFor(program: ghidra.program.model.listing.Program, log: ghidra.app.util.importer.MessageLog) -> ghidra.app.util.bin.format.golang.rtti.GoRttiMapper:
        """
        Returns a new {@link GoRttiMapper} for the specified program, or null if the binary
         is not a supported golang binary.
        @param program {@link Program}
        @param log
        @return new {@link GoRttiMapper}, or null if not a golang binary
        @throws IOException
        """
        ...

    def getProgram(self) -> ghidra.program.model.listing.Program: ...

    def getPtrSize(self) -> int: ...

    def getReader(self, position: long) -> ghidra.app.util.bin.BinaryReader: ...

    def getRecoveredType(self, typ: ghidra.app.util.bin.format.golang.rtti.types.GoType) -> ghidra.program.model.data.DataType: ...

    def getRecoveredTypesCp(self) -> ghidra.program.model.data.CategoryPath: ...

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

    def getUint32DT(self) -> ghidra.program.model.data.DataType: ...

    def getUintptrDT(self) -> ghidra.program.model.data.DataType: ...

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

    def recoverDataTypes(self, monitor: ghidra.util.task.TaskMonitor) -> None:
        """
        Converts all discovered golang rtti type records to Ghidra data types, placing them
         in the program's DTM in /golang-recovered
        @throws IOException
        @throws CancelledException
        """
        ...

    def registerStructure(self, clazz: java.lang.Class) -> None:
        """
        Registers a class that has {@link StructureMapping structure mapping} information.
        @param <T>
        @param clazz
        @throws IOException if the class's Ghidra structure data type could not be found
        """
        ...

    def registerStructures(self, __a0: List[object]) -> None: ...

    def resolveNameOff(self, ptrInModule: long, off: long) -> ghidra.app.util.bin.format.golang.rtti.GoName: ...

    def resolveTextOff(self, ptrInModule: long, off: long) -> ghidra.program.model.address.Address: ...

    def resolveTypeOff(self, ptrInModule: long, off: long) -> ghidra.app.util.bin.format.golang.rtti.types.GoType: ...

    def setMarkupTaskMonitor(self, monitor: ghidra.util.task.TaskMonitor) -> None: ...

    def toString(self) -> unicode: ...

    @overload
    def wait(self) -> None: ...

    @overload
    def wait(self, __a0: long) -> None: ...

    @overload
    def wait(self, __a0: long, __a1: int) -> None: ...

    @property
    def chanGoType(self) -> ghidra.app.util.bin.format.golang.rtti.types.GoType: ...

    @property
    def defaultVariableLengthStructCategoryPath(self) -> ghidra.program.model.data.CategoryPath: ...

    @property
    def firstModule(self) -> ghidra.app.util.bin.format.golang.rtti.GoModuledata: ...

    @property
    def genericSliceDT(self) -> ghidra.program.model.data.Structure: ...

    @property
    def golangVersion(self) -> ghidra.app.util.bin.format.golang.GoVer: ...

    @property
    def int32DT(self) -> ghidra.program.model.data.DataType: ...

    @property
    def mapGoType(self) -> ghidra.app.util.bin.format.golang.rtti.types.GoType: ...

    @property
    def ptrSize(self) -> int: ...

    @property
    def recoveredTypesCp(self) -> ghidra.program.model.data.CategoryPath: ...

    @property
    def uint32DT(self) -> ghidra.program.model.data.DataType: ...

    @property
    def uintptrDT(self) -> ghidra.program.model.data.DataType: ...