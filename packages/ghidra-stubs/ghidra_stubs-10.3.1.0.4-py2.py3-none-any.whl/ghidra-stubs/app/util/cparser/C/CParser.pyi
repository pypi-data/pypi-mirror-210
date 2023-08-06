from typing import List
import ghidra.app.util.cparser.C
import ghidra.app.util.cparser.C.CParser
import ghidra.program.model.data
import ghidra.util.task
import java.io
import java.lang
import java.util


class CParser(object, ghidra.app.util.cparser.C.CParserConstants):
    ALIGNAS: int = 45
    ALIGNOF: int = 46
    ASM: int = 52
    ASMBLOCK: int = 1
    ASMBLOCKB: int = 88
    ASMBLOCKP: int = 89
    ASM_SEMI: int = 90
    ATTRIBUTE: int = 49
    AUTO: int = 69
    BOOL: int = 66
    BREAK: int = 35
    CASE: int = 58
    CDECL: int = 38
    CHAR: int = 71
    CHARACTER_LITERAL: int = 16
    CONST: int = 37
    CONTINUE: int = 18
    DECIMAL_LITERAL: int = 11
    DECLSPEC: int = 39
    DEFAULT: int = 0
    DFLT: int = 23
    DIGIT: int = 85
    DO: int = 78
    DOUBLE: int = 24
    ELSE: int = 57
    ENUM: int = 68
    EOF: int = 0
    EXPONENT: int = 15
    EXTENSION: int = 50
    EXTERN: int = 28
    FAR: int = 74
    FASTCALL: int = 43
    FLOAT: int = 55
    FLOATING_POINT_LITERAL: int = 14
    FOR: int = 75
    GOTO: int = 72
    HEX_LITERAL: int = 12
    IDENTIFIER: int = 83
    IF: int = 77
    INLINE: int = 53
    INT: int = 76
    INT16: int = 61
    INT32: int = 62
    INT64: int = 63
    INT8: int = 60
    INTEGER_LITERAL: int = 10
    INTERFACE: int = 80
    LETTER: int = 84
    LINE: int = 81
    LINEALT: int = 82
    LINEBLOCK: int = 2
    LINENUMBER_LITERAL: int = 96
    LONG: int = 59
    NEAR: int = 73
    NORETURN: int = 44
    OBJC: int = 4
    OBJC2: int = 5
    OBJC2_END: int = 141
    OBJC2_IGNORE: int = 140
    OBJC_DIGIT: int = 128
    OBJC_IDENTIFIER: int = 126
    OBJC_IGNORE: int = 125
    OBJC_LETTER: int = 127
    OBJC_SEMI: int = 129
    OCTAL_LITERAL: int = 13
    PACKED: int = 48
    PATH_LITERAL: int = 95
    PCLOSE: int = 109
    PCOLON: int = 113
    PCOMMA: int = 114
    PDECIMAL_LITERAL: int = 116
    PDIGIT: int = 107
    PHEX_LITERAL: int = 117
    PIDENTIFIER: int = 105
    PINTEGER_LITERAL: int = 115
    PLETTER: int = 106
    PMINUS: int = 110
    POCTAL_LITERAL: int = 118
    POPEN: int = 108
    PPLUS: int = 111
    PRAGMA: int = 40
    PRAGMALINE: int = 3
    PROTOCOL: int = 79
    PSTAR: int = 112
    PSTRING_LITERAL: int = 119
    PTR32: int = 65
    PTR64: int = 64
    QUOTE_C: int = 29
    READABLETO: int = 41
    REGISTER: int = 20
    RESTRICT: int = 51
    RETURN: int = 27
    SHORT: int = 56
    SIGNED: int = 33
    SIZEOF: int = 25
    STATIC: int = 31
    STATICASSERT: int = 54
    STDCALL: int = 42
    STRING_LITERAL: int = 17
    STRUCT: int = 30
    SWITCH: int = 26
    THREADLOCAL: int = 32
    TYPEDEF: int = 22
    UNALIGNED: int = 47
    UNION: int = 36
    UNSIGNED: int = 21
    VOID: int = 70
    VOLATILE: int = 19
    W64: int = 67
    WHILE: int = 34
    jj_nt: ghidra.app.util.cparser.C.Token
    token: ghidra.app.util.cparser.C.Token
    tokenImage: List[unicode] = array(java.lang.String, [u'<EOF>', u'"\\ufeff"', u'" "', u'"\\f"', u'"\\t"', u'"\\n"', u'"\\r"', u'"\\\\"', u'<token of kind 8>', u'<token of kind 9>', u'<INTEGER_LITERAL>', u'<DECIMAL_LITERAL>', u'<HEX_LITERAL>', u'<OCTAL_LITERAL>', u'<FLOATING_POINT_LITERAL>', u'<EXPONENT>', u'<CHARACTER_LITERAL>', u'<STRING_LITERAL>', u'"continue"', u'<VOLATILE>', u'"register"', u'"unsigned"', u'"typedef"', u'"default"', u'"double"', u'"sizeof"', u'"switch"', u'"return"', u'"extern"', u'"\\"C\\""', u'"struct"', u'"static"', u'"_Thread_local"', u'<SIGNED>', u'"while"', u'"break"', u'"union"', u'<CONST>', u'<CDECL>', u'"__declspec"', u'<PRAGMA>', u'"__readableTo"', u'<STDCALL>', u'<FASTCALL>', u'"_Noreturn"', u'"_Alignas"', u'"_Alignof"', u'"__unaligned"', u'"__packed"', u'<ATTRIBUTE>', u'<EXTENSION>', u'<RESTRICT>', u'<ASM>', u'<INLINE>', u'<STATICASSERT>', u'"float"', u'"short"', u'"else"', u'"case"', u'"long"', u'"__int8"', u'"__int16"', u'"__int32"', u'"__int64"', u'"__ptr64"', u'"__ptr32"', u'"_Bool"', u'"__w64"', u'"enum"', u'"auto"', u'"void"', u'"char"', u'"goto"', u'"__near"', u'"__far"', u'"for"', u'"int"', u'"if"', u'"do"', u'"@protocol"', u'"@interface"', u'"#line"', u'<LINEALT>', u'<IDENTIFIER>', u'<LETTER>', u'<DIGIT>', u'" "', u'"\\t"', u'<ASMBLOCKB>', u'<ASMBLOCKP>', u'<ASM_SEMI>', u'" "', u'"\\f"', u'"\\t"', u'":"', u'<PATH_LITERAL>', u'<LINENUMBER_LITERAL>', u'" "', u'"\\f"', u'"\\t"', u'"\\n"', u'"\\r"', u'";"', u'<token of kind 103>', u'<token of kind 104>', u'<PIDENTIFIER>', u'<PLETTER>', u'<PDIGIT>', u'"("', u'")"', u'"-"', u'"+"', u'"*"', u'":"', u'","', u'<PINTEGER_LITERAL>', u'<PDECIMAL_LITERAL>', u'<PHEX_LITERAL>', u'<POCTAL_LITERAL>', u'<PSTRING_LITERAL>', u'" "', u'"\\f"', u'"\\t"', u'"\\n"', u'"\\r"', u'<OBJC_IGNORE>', u'<OBJC_IDENTIFIER>', u'<OBJC_LETTER>', u'<OBJC_DIGIT>', u'<OBJC_SEMI>', u'" "', u'"\\f"', u'"\\t"', u'"\\n"', u'"\\r"', u'"@private"', u'"@protected"', u'"@property"', u'"@optional"', u'"@required"', u'<OBJC2_IGNORE>', u'"@end"', u'"{"', u'"}"', u'";"', u'"("', u'")"', u'"["', u'"]"', u'","', u'":"', u'"="', u'"#"', u'"*"', u'"&"', u'"..."', u'"."', u'"+"', u'"-"', u'"*="', u'"/="', u'"%="', u'"+="', u'"-="', u'"<<="', u'">>="', u'"&="', u'"^="', u'"|="', u'"?"', u'"||"', u'"&&"', u'"|"', u'"^"', u'"=="', u'"!="', u'"<"', u'">"', u'"<="', u'">="', u'"<<"', u'">>"', u'"/"', u'"%"', u'"++"', u'"--"', u'"~"', u'"!"', u'"->"'])
    token_source: ghidra.app.util.cparser.C.CParserTokenManager



    @overload
    def __init__(self): ...

    @overload
    def __init__(self, tm: ghidra.app.util.cparser.C.CParserTokenManager):
        """
        Constructor with generated Token Manager.
        """
        ...

    @overload
    def __init__(self, dtmgr: ghidra.program.model.data.DataTypeManager): ...

    @overload
    def __init__(self, stream: java.io.InputStream):
        """
        Constructor with InputStream.
        """
        ...

    @overload
    def __init__(self, stream: java.io.Reader):
        """
        Constructor.
        """
        ...

    @overload
    def __init__(self, stream: java.io.InputStream, encoding: unicode):
        """
        Constructor with InputStream and supplied encoding
        """
        ...

    @overload
    def __init__(self, dtmgr: ghidra.program.model.data.DataTypeManager, storeDataType: bool, subDTMgrs: List[ghidra.program.model.data.DataTypeManager]): ...



    def ANDExpression(self) -> object: ...

    def AbstractDeclarator(self, dt: ghidra.app.util.cparser.C.Declaration) -> ghidra.app.util.cparser.C.Declaration: ...

    def AdditiveExpression(self) -> object: ...

    def AlignmentSpecifier(self) -> None: ...

    def ArgumentExpressionList(self) -> None: ...

    def AsmLine(self) -> None: ...

    def AsmStatement(self) -> None: ...

    def AssignmentExpression(self) -> object: ...

    def AssignmentOperator(self) -> None: ...

    def AttributeList(self, dec: ghidra.app.util.cparser.C.Declaration) -> None: ...

    def AttributeSpec(self, dec: ghidra.app.util.cparser.C.Declaration) -> None: ...

    def AttributeSpecList(self, dec: ghidra.app.util.cparser.C.Declaration) -> None: ...

    def AttributeToken(self, dec: ghidra.app.util.cparser.C.Declaration) -> None: ...

    def BuiltInDeclarationSpecifier(self, dec: ghidra.app.util.cparser.C.Declaration) -> ghidra.app.util.cparser.C.Declaration: ...

    def BuiltInTypeSpecifier(self, dec: ghidra.app.util.cparser.C.Declaration) -> ghidra.app.util.cparser.C.Declaration: ...

    def CastExpression(self) -> object: ...

    def CompoundStatement(self) -> None: ...

    def ConditionalExpression(self) -> object: ...

    def Constant(self) -> object: ...

    def ConstantExpression(self) -> object: ...

    def DeclConstant(self) -> None: ...

    def DeclSpec(self, dec: ghidra.app.util.cparser.C.Declaration) -> None: ...

    def DeclSpecifier(self, dec: ghidra.app.util.cparser.C.Declaration) -> None: ...

    def Declaration(self) -> ghidra.app.util.cparser.C.Declaration: ...

    def DeclarationList(self) -> None: ...

    def DeclarationSpecifiers(self, specDT: ghidra.app.util.cparser.C.Declaration) -> ghidra.app.util.cparser.C.Declaration: ...

    def Declarator(self, dt: ghidra.app.util.cparser.C.Declaration, container: ghidra.program.model.data.DataType) -> ghidra.app.util.cparser.C.Declaration: ...

    def Designation(self) -> None: ...

    def Designator(self) -> None: ...

    def DesignatorList(self) -> None: ...

    def DirectAbstractDeclarator(self, dt: ghidra.app.util.cparser.C.Declaration) -> ghidra.app.util.cparser.C.Declaration: ...

    def DirectDeclarator(self, dt: ghidra.app.util.cparser.C.Declaration, container: ghidra.program.model.data.DataType) -> ghidra.app.util.cparser.C.Declaration: ...

    def EnumSpecifier(self) -> ghidra.program.model.data.DataType: ...

    def Enumerator(self, __a0: java.util.ArrayList, __a1: int) -> int: ...

    def EnumeratorList(self) -> List[ghidra.app.util.cparser.C.CParser.EnumMember]: ...

    def EqualityExpression(self) -> object: ...

    def ExclusiveORExpression(self) -> object: ...

    def Expression(self) -> object: ...

    def ExpressionStatement(self) -> None: ...

    def ExternalDeclaration(self) -> None: ...

    def FunctionDefinition(self) -> None: ...

    def IdentifierList(self, funcDT: ghidra.program.model.data.FunctionDefinitionDataType, retDT: ghidra.program.model.data.DataType) -> None: ...

    def InclusiveORExpression(self) -> object: ...

    def InitDeclarator(self, dt: ghidra.app.util.cparser.C.Declaration) -> None: ...

    def InitDeclaratorList(self, dt: ghidra.app.util.cparser.C.Declaration) -> None: ...

    def Initializer(self) -> None: ...

    def InitializerList(self) -> None: ...

    def IterationStatement(self) -> None: ...

    def JumpStatement(self) -> None: ...

    def LabeledStatement(self) -> None: ...

    def LineDef(self) -> None: ...

    def LogicalANDExpression(self) -> object: ...

    def LogicalORExpression(self) -> object: ...

    def MultiLineString(self) -> ghidra.app.util.cparser.C.Token: ...

    def MultiplicativeExpression(self) -> object: ...

    def ObjcDef(self) -> ghidra.program.model.data.DataType: ...

    def ParameterDeclaration(self, __a0: java.util.ArrayList) -> None: ...

    def ParameterList(self) -> List[ghidra.app.util.cparser.C.Declaration]: ...

    def ParameterTypeList(self, funcDT: ghidra.program.model.data.FunctionDefinitionDataType, retDT: ghidra.program.model.data.DataType) -> ghidra.app.util.cparser.C.Declaration: ...

    def Pointer(self, dec: ghidra.app.util.cparser.C.Declaration) -> ghidra.app.util.cparser.C.Declaration: ...

    def PostfixExpression(self) -> object: ...

    def PragmaConstant(self) -> ghidra.app.util.cparser.C.Token: ...

    def PragmaSpec(self) -> None: ...

    def PragmaSpecifier(self) -> None: ...

    def PrimaryExpression(self) -> object: ...

    @overload
    def ReInit(self, tm: ghidra.app.util.cparser.C.CParserTokenManager) -> None:
        """
        Reinitialise.
        """
        ...

    @overload
    def ReInit(self, stream: java.io.InputStream) -> None:
        """
        Reinitialise.
        """
        ...

    @overload
    def ReInit(self, stream: java.io.Reader) -> None:
        """
        Reinitialise.
        """
        ...

    @overload
    def ReInit(self, stream: java.io.InputStream, encoding: unicode) -> None:
        """
        Reinitialise.
        """
        ...

    def RelationalExpression(self) -> object: ...

    def SelectionStatement(self) -> None: ...

    def ShiftExpression(self) -> object: ...

    def SpecifierQualifierList(self) -> ghidra.app.util.cparser.C.Declaration: ...

    def Statement(self) -> None: ...

    def StatementList(self) -> None: ...

    def StaticAssert(self) -> None: ...

    def StorageClassSpecifier(self, specDT: ghidra.app.util.cparser.C.Declaration) -> ghidra.app.util.cparser.C.Declaration: ...

    def StructDeclaration(self, comp: ghidra.program.model.data.Composite, compositeHandler: ghidra.app.util.cparser.C.CompositeHandler) -> None: ...

    def StructDeclarationList(self, comp: ghidra.program.model.data.Composite) -> None: ...

    def StructDeclarator(self, dt: ghidra.app.util.cparser.C.Declaration, comp: ghidra.program.model.data.Composite, compositeHandler: ghidra.app.util.cparser.C.CompositeHandler) -> None: ...

    def StructDeclaratorList(self, dt: ghidra.app.util.cparser.C.Declaration, comp: ghidra.program.model.data.Composite, compositeHandler: ghidra.app.util.cparser.C.CompositeHandler) -> None: ...

    def StructOrUnion(self) -> ghidra.program.model.data.Composite: ...

    def StructOrUnionSpecifier(self) -> ghidra.program.model.data.DataType: ...

    def SubIdent(self, dec: ghidra.app.util.cparser.C.Declaration) -> None: ...

    def TranslationUnit(self) -> None: ...

    def TypeName(self) -> ghidra.app.util.cparser.C.Declaration: ...

    def TypeQualifier(self, dec: ghidra.app.util.cparser.C.Declaration) -> ghidra.app.util.cparser.C.Declaration: ...

    def TypeQualifierList(self, dec: ghidra.app.util.cparser.C.Declaration) -> ghidra.app.util.cparser.C.Declaration: ...

    def TypeSpecifier(self, dec: ghidra.app.util.cparser.C.Declaration) -> ghidra.app.util.cparser.C.Declaration: ...

    def TypedefName(self) -> ghidra.program.model.data.DataType: ...

    def UnaryExpression(self) -> object: ...

    def UnaryOperator(self) -> None: ...

    def didParseSucceed(self) -> bool: ...

    def disable_tracing(self) -> None:
        """
        Disable tracing.
        """
        ...

    def enable_tracing(self) -> None:
        """
        Enable tracing.
        """
        ...

    def equals(self, __a0: object) -> bool: ...

    def generateParseException(self) -> ghidra.app.util.cparser.C.ParseException:
        """
        Generate ParseException.
        """
        ...

    def getClass(self) -> java.lang.Class: ...

    def getComposites(self) -> java.util.Map:
        """
        Get composite definitions
        @return Composite (structure/union) definitions
        """
        ...

    def getDataTypeManager(self) -> ghidra.program.model.data.DataTypeManager:
        """
        Get the data type manager
        @return 
        """
        ...

    def getDeclarations(self) -> java.util.Map:
        """
        Get Global variable declarations
        @return 
        """
        ...

    def getEnums(self) -> java.util.Map:
        """
        Get Defined Enumerations
        @return Defined enumeration names
        """
        ...

    def getFunctions(self) -> java.util.Map:
        """
        Get Function signatures
        @return Function signatures
        """
        ...

    def getLastDataType(self) -> ghidra.program.model.data.DataType:
        """
        @return the last data type parsed
        """
        ...

    def getNextToken(self) -> ghidra.app.util.cparser.C.Token:
        """
        Get the next Token.
        """
        ...

    def getParseMessages(self) -> unicode: ...

    def getToken(self, index: int) -> ghidra.app.util.cparser.C.Token:
        """
        Get the specific Token.
        """
        ...

    def getTypes(self) -> java.util.Map:
        """
        Get Type definitions
        @return Type definitions
        """
        ...

    def hashCode(self) -> int: ...

    @staticmethod
    def main(args: List[unicode]) -> None: ...

    def notify(self) -> None: ...

    def notifyAll(self) -> None: ...

    @overload
    def parse(self, str: unicode) -> ghidra.program.model.data.DataType: ...

    @overload
    def parse(self, fis: java.io.InputStream) -> None: ...

    def setMonitor(self, monitor: ghidra.util.task.TaskMonitor) -> None: ...

    def setParseFileName(self, fName: unicode) -> None: ...

    def toString(self) -> unicode: ...

    @overload
    def wait(self) -> None: ...

    @overload
    def wait(self, __a0: long) -> None: ...

    @overload
    def wait(self, __a0: long, __a1: int) -> None: ...

    @property
    def composites(self) -> java.util.Map: ...

    @property
    def dataTypeManager(self) -> ghidra.program.model.data.DataTypeManager: ...

    @property
    def declarations(self) -> java.util.Map: ...

    @property
    def enums(self) -> java.util.Map: ...

    @property
    def functions(self) -> java.util.Map: ...

    @property
    def lastDataType(self) -> ghidra.program.model.data.DataType: ...

    @property
    def monitor(self) -> None: ...  # No getter available.

    @monitor.setter
    def monitor(self, value: ghidra.util.task.TaskMonitor) -> None: ...

    @property
    def nextToken(self) -> ghidra.app.util.cparser.C.Token: ...

    @property
    def parseFileName(self) -> None: ...  # No getter available.

    @parseFileName.setter
    def parseFileName(self, value: unicode) -> None: ...

    @property
    def parseMessages(self) -> unicode: ...

    @property
    def types(self) -> java.util.Map: ...