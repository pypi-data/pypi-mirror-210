from typing import List
import ghidra.trace.model
import ghidra.trace.model.target
import ghidra.trace.model.target.annot
import java.lang
import java.util


class TraceObjectInterfaceUtils(java.lang.Enum):








    @overload
    def compareTo(self, __a0: java.lang.Enum) -> int: ...

    @overload
    def compareTo(self, __a0: object) -> int: ...

    def describeConstable(self) -> java.util.Optional: ...

    def equals(self, __a0: object) -> bool: ...

    def getClass(self) -> java.lang.Class: ...

    def getDeclaringClass(self) -> java.lang.Class: ...

    @staticmethod
    def getFixedKeys(__a0: java.lang.Class) -> java.util.Collection: ...

    @staticmethod
    def getShortName(__a0: java.lang.Class) -> unicode: ...

    @staticmethod
    def getValue(__a0: ghidra.trace.model.target.TraceObject, __a1: long, __a2: unicode, __a3: java.lang.Class, __a4: object) -> object: ...

    def hashCode(self) -> int: ...

    def name(self) -> unicode: ...

    def notify(self) -> None: ...

    def notifyAll(self) -> None: ...

    def ordinal(self) -> int: ...

    @staticmethod
    def requireAnnotation(__a0: java.lang.Class) -> ghidra.trace.model.target.annot.TraceObjectInfo: ...

    @staticmethod
    def setLifespan(__a0: java.lang.Class, __a1: ghidra.trace.model.target.TraceObject, __a2: ghidra.trace.model.Lifespan) -> None: ...

    def toString(self) -> unicode: ...

    @staticmethod
    def toTargetIf(__a0: java.lang.Class) -> java.lang.Class: ...

    @overload
    @staticmethod
    def valueOf(__a0: unicode) -> ghidra.trace.model.target.annot.TraceObjectInterfaceUtils: ...

    @overload
    @staticmethod
    def valueOf(__a0: java.lang.Class, __a1: unicode) -> java.lang.Enum: ...

    @staticmethod
    def values() -> List[ghidra.trace.model.target.annot.TraceObjectInterfaceUtils]: ...

    @overload
    def wait(self) -> None: ...

    @overload
    def wait(self, __a0: long) -> None: ...

    @overload
    def wait(self, __a0: long, __a1: int) -> None: ...

