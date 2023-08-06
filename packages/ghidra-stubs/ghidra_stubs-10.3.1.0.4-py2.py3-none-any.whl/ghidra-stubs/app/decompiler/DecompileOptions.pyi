from typing import List
import ghidra.app.decompiler
import ghidra.app.decompiler.DecompileOptions
import ghidra.framework.options
import ghidra.framework.plugintool
import ghidra.program.model.lang
import ghidra.program.model.listing
import ghidra.program.model.pcode
import java.awt
import java.lang
import java.util


class DecompileOptions(object):
    """
    Configuration options for the decompiler
     This stores the options and can create an XML
     string to be sent to the decompiler process
    """

    DEFAULT_FONT_ID: unicode = u'font.decompiler'
    SUGGESTED_DECOMPILE_TIMEOUT_SECS: int = 30
    SUGGESTED_MAX_INSTRUCTIONS: int = 100000
    SUGGESTED_MAX_PAYLOAD_BYTES: int = 50




    class AliasBlockEnum(java.lang.Enum):
        All: ghidra.app.decompiler.DecompileOptions.AliasBlockEnum = All Data-types
        Array: ghidra.app.decompiler.DecompileOptions.AliasBlockEnum = Arrays and Structures
        None: ghidra.app.decompiler.DecompileOptions.AliasBlockEnum = None
        Struct: ghidra.app.decompiler.DecompileOptions.AliasBlockEnum = Structures







        @overload
        def compareTo(self, __a0: java.lang.Enum) -> int: ...

        @overload
        def compareTo(self, __a0: object) -> int: ...

        def describeConstable(self) -> java.util.Optional: ...

        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def getDeclaringClass(self) -> java.lang.Class: ...

        def getOptionString(self) -> unicode: ...

        def hashCode(self) -> int: ...

        def name(self) -> unicode: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        def ordinal(self) -> int: ...

        def toString(self) -> unicode: ...

        @overload
        @staticmethod
        def valueOf(__a0: unicode) -> ghidra.app.decompiler.DecompileOptions.AliasBlockEnum: ...

        @overload
        @staticmethod
        def valueOf(__a0: java.lang.Class, __a1: unicode) -> java.lang.Enum: ...

        @staticmethod
        def values() -> List[ghidra.app.decompiler.DecompileOptions.AliasBlockEnum]: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @property
        def optionString(self) -> unicode: ...




    class IntegerFormatEnum(java.lang.Enum):
        BestFit: ghidra.app.decompiler.DecompileOptions.IntegerFormatEnum = Best Fit
        Decimal: ghidra.app.decompiler.DecompileOptions.IntegerFormatEnum = Force Decimal
        Hexadecimal: ghidra.app.decompiler.DecompileOptions.IntegerFormatEnum = Force Hexadecimal







        @overload
        def compareTo(self, __a0: java.lang.Enum) -> int: ...

        @overload
        def compareTo(self, __a0: object) -> int: ...

        def describeConstable(self) -> java.util.Optional: ...

        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def getDeclaringClass(self) -> java.lang.Class: ...

        def getOptionString(self) -> unicode: ...

        def hashCode(self) -> int: ...

        def name(self) -> unicode: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        def ordinal(self) -> int: ...

        def toString(self) -> unicode: ...

        @overload
        @staticmethod
        def valueOf(__a0: unicode) -> ghidra.app.decompiler.DecompileOptions.IntegerFormatEnum: ...

        @overload
        @staticmethod
        def valueOf(__a0: java.lang.Class, __a1: unicode) -> java.lang.Enum: ...

        @staticmethod
        def values() -> List[ghidra.app.decompiler.DecompileOptions.IntegerFormatEnum]: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @property
        def optionString(self) -> unicode: ...




    class NamespaceStrategy(java.lang.Enum):
        All: ghidra.app.decompiler.DecompileOptions.NamespaceStrategy = Always
        Minimal: ghidra.app.decompiler.DecompileOptions.NamespaceStrategy = Minimally
        Never: ghidra.app.decompiler.DecompileOptions.NamespaceStrategy = Never







        @overload
        def compareTo(self, __a0: java.lang.Enum) -> int: ...

        @overload
        def compareTo(self, __a0: object) -> int: ...

        def describeConstable(self) -> java.util.Optional: ...

        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def getDeclaringClass(self) -> java.lang.Class: ...

        def getOptionString(self) -> unicode: ...

        def hashCode(self) -> int: ...

        def name(self) -> unicode: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        def ordinal(self) -> int: ...

        def toString(self) -> unicode: ...

        @overload
        @staticmethod
        def valueOf(__a0: unicode) -> ghidra.app.decompiler.DecompileOptions.NamespaceStrategy: ...

        @overload
        @staticmethod
        def valueOf(__a0: java.lang.Class, __a1: unicode) -> java.lang.Enum: ...

        @staticmethod
        def values() -> List[ghidra.app.decompiler.DecompileOptions.NamespaceStrategy]: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...

        @property
        def optionString(self) -> unicode: ...




    class CommentStyleEnum(java.lang.Enum):
        CPPStyle: ghidra.app.decompiler.DecompileOptions.CommentStyleEnum = // C++-style comments
        CStyle: ghidra.app.decompiler.DecompileOptions.CommentStyleEnum = /* C-style comments */







        @overload
        def compareTo(self, __a0: java.lang.Enum) -> int: ...

        @overload
        def compareTo(self, __a0: object) -> int: ...

        def describeConstable(self) -> java.util.Optional: ...

        def equals(self, __a0: object) -> bool: ...

        def getClass(self) -> java.lang.Class: ...

        def getDeclaringClass(self) -> java.lang.Class: ...

        def hashCode(self) -> int: ...

        def name(self) -> unicode: ...

        def notify(self) -> None: ...

        def notifyAll(self) -> None: ...

        def ordinal(self) -> int: ...

        def toString(self) -> unicode: ...

        @overload
        @staticmethod
        def valueOf(__a0: unicode) -> ghidra.app.decompiler.DecompileOptions.CommentStyleEnum: ...

        @overload
        @staticmethod
        def valueOf(__a0: java.lang.Class, __a1: unicode) -> java.lang.Enum: ...

        @staticmethod
        def values() -> List[ghidra.app.decompiler.DecompileOptions.CommentStyleEnum]: ...

        @overload
        def wait(self) -> None: ...

        @overload
        def wait(self, __a0: long) -> None: ...

        @overload
        def wait(self, __a0: long, __a1: int) -> None: ...



    def __init__(self): ...



    def encode(self, encoder: ghidra.program.model.pcode.Encoder, iface: ghidra.app.decompiler.DecompInterface) -> None:
        """
        Encode all the configuration options to a stream for the decompiler process.
         This object is global to all decompile processes so we can tailor to the specific process
         by passing in the interface.
        @param encoder is the stream encoder
        @param iface specific DecompInterface being sent options
        @throws IOException for errors writing to the underlying stream
        """
        ...

    def equals(self, __a0: object) -> bool: ...

    def getBackgroundColor(self) -> java.awt.Color:
        """
        @return the background color for the decompiler window
        """
        ...

    def getCacheSize(self) -> int: ...

    def getClass(self) -> java.lang.Class: ...

    def getCommentColor(self) -> java.awt.Color:
        """
        @return color used to display comments
        """
        ...

    def getCommentStyle(self) -> ghidra.app.decompiler.DecompileOptions.CommentStyleEnum: ...

    def getConstantColor(self) -> java.awt.Color:
        """
        @return color associated with constant tokens
        """
        ...

    def getCurrentVariableHighlightColor(self) -> java.awt.Color:
        """
        @return the color used display the current highlighted variable
        """
        ...

    def getDefaultColor(self) -> java.awt.Color:
        """
        @return color for generic syntax or other unspecified tokens
        """
        ...

    def getDefaultFont(self) -> java.awt.Font: ...

    def getDefaultTimeout(self) -> int: ...

    def getDisplayLanguage(self) -> ghidra.program.model.lang.DecompilerLanguage: ...

    def getErrorColor(self) -> java.awt.Color:
        """
        @return color used on tokens that need to warn of an error or other unusual conditions
        """
        ...

    def getFunctionColor(self) -> java.awt.Color:
        """
        @return color associated with a function name token
        """
        ...

    def getGlobalColor(self) -> java.awt.Color:
        """
        @return color associated with global variable tokens
        """
        ...

    def getKeywordColor(self) -> java.awt.Color:
        """
        @return color associated with keyword tokens
        """
        ...

    def getMaxInstructions(self) -> int: ...

    def getMaxPayloadMBytes(self) -> int: ...

    def getMaxWidth(self) -> int: ...

    def getMiddleMouseHighlightButton(self) -> int: ...

    def getMiddleMouseHighlightColor(self) -> java.awt.Color:
        """
        @return color used to highlight token(s) selected with a middle button clock
        """
        ...

    def getParameterColor(self) -> java.awt.Color:
        """
        @return color associated with parameter tokens
        """
        ...

    def getProtoEvalModel(self) -> unicode: ...

    def getSearchHighlightColor(self) -> java.awt.Color:
        """
        @return color used to highlight search results
        """
        ...

    def getSpecialColor(self) -> java.awt.Color:
        """
        @return color associated with volatile variables or other special tokens
        """
        ...

    def getTypeColor(self) -> java.awt.Color:
        """
        @return color associated with data-type tokens
        """
        ...

    def getVariableColor(self) -> java.awt.Color:
        """
        @return color associated with (local) variable tokens
        """
        ...

    def grabFromProgram(self, program: ghidra.program.model.listing.Program) -> None:
        """
        Grab all the decompiler options from the program specifically
         and cache them in this object.
        @param program the program whose "program options" are relevant to the decompiler
        """
        ...

    def grabFromToolAndProgram(self, ownerPlugin: ghidra.framework.plugintool.Plugin, opt: ghidra.framework.options.ToolOptions, program: ghidra.program.model.listing.Program) -> None:
        """
        Grab all the decompiler options from various sources within a specific tool and program
         and cache them in this object.
        @param ownerPlugin the plugin that owns the "tool options" for the decompiler
        @param opt the Options object that contains the "tool options" specific to the decompiler
        @param program the program whose "program options" are relevant to the decompiler
        """
        ...

    def hashCode(self) -> int: ...

    def isConventionPrint(self) -> bool: ...

    def isDisplayLineNumbers(self) -> bool: ...

    def isEOLCommentIncluded(self) -> bool: ...

    def isEliminateUnreachable(self) -> bool: ...

    def isHeadCommentIncluded(self) -> bool: ...

    def isNoCastPrint(self) -> bool: ...

    def isPLATECommentIncluded(self) -> bool: ...

    def isPOSTCommentIncluded(self) -> bool: ...

    def isPRECommentIncluded(self) -> bool: ...

    def isSimplifyDoublePrecision(self) -> bool: ...

    def isWARNCommentIncluded(self) -> bool: ...

    def notify(self) -> None: ...

    def notifyAll(self) -> None: ...

    def registerOptions(self, ownerPlugin: ghidra.framework.plugintool.Plugin, opt: ghidra.framework.options.ToolOptions, program: ghidra.program.model.listing.Program) -> None:
        """
        This registers all the decompiler tool options with ghidra, and has the side effect of
         pulling all the current values for the options if they exist
        @param ownerPlugin the plugin to which the options should be registered
        @param opt the options object to register with
        @param program the program
        """
        ...

    def setCommentStyle(self, commentStyle: ghidra.app.decompiler.DecompileOptions.CommentStyleEnum) -> None: ...

    def setConventionPrint(self, conventionPrint: bool) -> None: ...

    def setDefaultTimeout(self, timeout: int) -> None: ...

    def setDisplayLanguage(self, val: ghidra.program.model.lang.DecompilerLanguage) -> None: ...

    def setEOLCommentIncluded(self, commentEOLInclude: bool) -> None: ...

    def setEliminateUnreachable(self, eliminateUnreachable: bool) -> None: ...

    def setHeadCommentIncluded(self, commentHeadInclude: bool) -> None: ...

    def setMaxInstructions(self, num: int) -> None: ...

    def setMaxPayloadMBytes(self, mbytes: int) -> None: ...

    def setMaxWidth(self, maxwidth: int) -> None: ...

    def setNoCastPrint(self, noCastPrint: bool) -> None: ...

    def setPLATECommentIncluded(self, commentPLATEInclude: bool) -> None: ...

    def setPOSTCommentIncluded(self, commentPOSTInclude: bool) -> None: ...

    def setPRECommentIncluded(self, commentPREInclude: bool) -> None: ...

    def setProtoEvalModel(self, protoEvalModel: unicode) -> None: ...

    def setSimplifyDoublePrecision(self, simplifyDoublePrecision: bool) -> None: ...

    def setWARNCommentIncluded(self, commentWARNInclude: bool) -> None: ...

    def toString(self) -> unicode: ...

    @overload
    def wait(self) -> None: ...

    @overload
    def wait(self, __a0: long) -> None: ...

    @overload
    def wait(self, __a0: long, __a1: int) -> None: ...

    @property
    def EOLCommentIncluded(self) -> bool: ...

    @EOLCommentIncluded.setter
    def EOLCommentIncluded(self, value: bool) -> None: ...

    @property
    def PLATECommentIncluded(self) -> bool: ...

    @PLATECommentIncluded.setter
    def PLATECommentIncluded(self, value: bool) -> None: ...

    @property
    def POSTCommentIncluded(self) -> bool: ...

    @POSTCommentIncluded.setter
    def POSTCommentIncluded(self, value: bool) -> None: ...

    @property
    def PRECommentIncluded(self) -> bool: ...

    @PRECommentIncluded.setter
    def PRECommentIncluded(self, value: bool) -> None: ...

    @property
    def WARNCommentIncluded(self) -> bool: ...

    @WARNCommentIncluded.setter
    def WARNCommentIncluded(self, value: bool) -> None: ...

    @property
    def backgroundColor(self) -> java.awt.Color: ...

    @property
    def cacheSize(self) -> int: ...

    @property
    def commentColor(self) -> java.awt.Color: ...

    @property
    def commentStyle(self) -> ghidra.app.decompiler.DecompileOptions.CommentStyleEnum: ...

    @commentStyle.setter
    def commentStyle(self, value: ghidra.app.decompiler.DecompileOptions.CommentStyleEnum) -> None: ...

    @property
    def constantColor(self) -> java.awt.Color: ...

    @property
    def conventionPrint(self) -> bool: ...

    @conventionPrint.setter
    def conventionPrint(self, value: bool) -> None: ...

    @property
    def currentVariableHighlightColor(self) -> java.awt.Color: ...

    @property
    def defaultColor(self) -> java.awt.Color: ...

    @property
    def defaultFont(self) -> java.awt.Font: ...

    @property
    def defaultTimeout(self) -> int: ...

    @defaultTimeout.setter
    def defaultTimeout(self, value: int) -> None: ...

    @property
    def displayLanguage(self) -> ghidra.program.model.lang.DecompilerLanguage: ...

    @displayLanguage.setter
    def displayLanguage(self, value: ghidra.program.model.lang.DecompilerLanguage) -> None: ...

    @property
    def displayLineNumbers(self) -> bool: ...

    @property
    def eliminateUnreachable(self) -> bool: ...

    @eliminateUnreachable.setter
    def eliminateUnreachable(self, value: bool) -> None: ...

    @property
    def errorColor(self) -> java.awt.Color: ...

    @property
    def functionColor(self) -> java.awt.Color: ...

    @property
    def globalColor(self) -> java.awt.Color: ...

    @property
    def headCommentIncluded(self) -> bool: ...

    @headCommentIncluded.setter
    def headCommentIncluded(self, value: bool) -> None: ...

    @property
    def keywordColor(self) -> java.awt.Color: ...

    @property
    def maxInstructions(self) -> int: ...

    @maxInstructions.setter
    def maxInstructions(self, value: int) -> None: ...

    @property
    def maxPayloadMBytes(self) -> int: ...

    @maxPayloadMBytes.setter
    def maxPayloadMBytes(self, value: int) -> None: ...

    @property
    def maxWidth(self) -> int: ...

    @maxWidth.setter
    def maxWidth(self, value: int) -> None: ...

    @property
    def middleMouseHighlightButton(self) -> int: ...

    @property
    def middleMouseHighlightColor(self) -> java.awt.Color: ...

    @property
    def noCastPrint(self) -> bool: ...

    @noCastPrint.setter
    def noCastPrint(self, value: bool) -> None: ...

    @property
    def parameterColor(self) -> java.awt.Color: ...

    @property
    def protoEvalModel(self) -> unicode: ...

    @protoEvalModel.setter
    def protoEvalModel(self, value: unicode) -> None: ...

    @property
    def searchHighlightColor(self) -> java.awt.Color: ...

    @property
    def simplifyDoublePrecision(self) -> bool: ...

    @simplifyDoublePrecision.setter
    def simplifyDoublePrecision(self, value: bool) -> None: ...

    @property
    def specialColor(self) -> java.awt.Color: ...

    @property
    def typeColor(self) -> java.awt.Color: ...

    @property
    def variableColor(self) -> java.awt.Color: ...