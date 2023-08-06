from typing import List
import ghidra.framework.options
import ghidra.framework.plugintool
import java.lang
import java.lang.invoke


class AutoConfigState(object):





    class IntArrayConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.IntArrayConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$IntArrayConfigFieldCodec@3924bc6b



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[int]) -> List[int]: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[int]) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class LongArrayConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.LongArrayConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$LongArrayConfigFieldCodec@5276b1a7



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[long]) -> List[long]: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[long]) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class StringConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.StringConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$StringConfigFieldCodec@aae469



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: unicode) -> unicode: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: unicode) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class LongConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.LongConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$LongConfigFieldCodec@43808dad



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: long) -> long: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: long) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class IntConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.IntConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$IntConfigFieldCodec@61eec4c



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: int) -> int: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class FloatArrayConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.FloatArrayConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$FloatArrayConfigFieldCodec@233430f



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[float]) -> List[float]: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[float]) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class ShortArrayConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.ShortArrayConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$ShortArrayConfigFieldCodec@24342fc4



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[int]) -> List[int]: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[int]) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class StringArrayConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.StringArrayConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$StringArrayConfigFieldCodec@338e4b06



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[unicode]) -> List[unicode]: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[unicode]) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class ByteArrayConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.ByteArrayConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$ByteArrayConfigFieldCodec@2d4e4442



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[int]) -> List[int]: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[int]) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class BooleanArrayConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.BooleanArrayConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$BooleanArrayConfigFieldCodec@2d57c8bd



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[bool]) -> List[bool]: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[bool]) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class DoubleConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.DoubleConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$DoubleConfigFieldCodec@52619d6e



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: float) -> float: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: float) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class ByteConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.ByteConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$ByteConfigFieldCodec@2e8d086e



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: int) -> int: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class ClassHandler(object):








        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        def readConfigState(self, __a0: object, __a1: ghidra.framework.options.SaveState) -> None: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        def writeConfigState(self, __a0: object, __a1: ghidra.framework.options.SaveState) -> None: ...






    class ConfigStateField(object):








        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        @staticmethod
        def getCodecByType(__a0: java.lang.Class) -> ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec: ...

        @staticmethod
        def getState(__a0: ghidra.framework.options.SaveState, __a1: java.lang.Class, __a2: unicode) -> object: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @staticmethod
        def putState(__a0: ghidra.framework.options.SaveState, __a1: java.lang.Class, __a2: unicode, __a3: object) -> None: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...






    class ShortConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.ShortConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$ShortConfigFieldCodec@72874a78



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: int) -> int: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class ConfigFieldCodec(object):








        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class FloatConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.FloatConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$FloatConfigFieldCodec@25e5d368



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: float) -> float: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: float) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class DoubleArrayConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.DoubleArrayConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$DoubleArrayConfigFieldCodec@5c8cb64d



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[float]) -> List[float]: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: List[float]) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class EnumConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.EnumConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$EnumConfigFieldCodec@69efba5c



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: java.lang.Enum) -> java.lang.Enum: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: java.lang.Enum) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...






    class BooleanConfigFieldCodec(object, ghidra.framework.plugintool.AutoConfigState.ConfigFieldCodec):
        INSTANCE: ghidra.framework.plugintool.AutoConfigState.BooleanConfigFieldCodec = ghidra.framework.plugintool.AutoConfigState$BooleanConfigFieldCodec@6fb23c80



        def __init__(self): ...



        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: bool) -> bool: ...

        @overload
        def read(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> object: ...

        def toString(self) -> unicode: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: bool) -> None: ...

        @overload
        def write(self, __a0: ghidra.framework.options.SaveState, __a1: unicode, __a2: object) -> None: ...







    def equals(self, __a0: object) -> bool: ...

    def getClass(self) -> java.lang.Class: ...

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

    @staticmethod
    def wireHandler(__a0: java.lang.Class, __a1: java.lang.invoke.MethodHandles.Lookup) -> ghidra.framework.plugintool.AutoConfigState.ClassHandler: ...

