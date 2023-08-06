import ghidra.app.util.cparser.C
import java.io
import java.lang


class CParserTokenManager(object, ghidra.app.util.cparser.C.CParserConstants):
    """
    Token Manager.
    """

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
    debugStream: java.io.PrintStream
    jjnewLexState: List[int] = array('i', [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 4, 4, 2, 2, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, 0, -1, -1, -1, -1, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 5, 5, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])
    jjstrLiteralImages: List[unicode] = array(java.lang.String, [u'', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, u'continue', None, u'register', u'unsigned', u'typedef', u'default', u'double', u'sizeof', u'switch', u'return', u'extern', u'"C"', u'struct', u'static', u'_Thread_local', None, u'while', u'break', u'union', None, None, u'__declspec', None, u'__readableTo', None, None, u'_Noreturn', u'_Alignas', u'_Alignof', u'__unaligned', u'__packed', None, None, None, None, None, None, u'float', u'short', u'else', u'case', u'long', u'__int8', u'__int16', u'__int32', u'__int64', u'__ptr64', u'__ptr32', u'_Bool', u'__w64', u'enum', u'auto', u'void', u'char', u'goto', u'__near', u'__far', u'for', u'int', u'if', u'do', u'@protocol', u'@interface', u'#line', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, u'(', u')', u'-', u'+', u'*', u':', u',', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, u'@end', u'{', u'}', u';', u'(', u')', u'[', u']', u',', u':', u'=', u'#', u'*', u'&', u'...', u'.', u'+', u'-', u'*=', u'/=', u'%=', u'+=', u'-=', u'<<=', u'>>=', u'&=', u'^=', u'|=', u'?', u'||', u'&&', u'|', u'^', u'==', u'!=', u'<', u'>', u'<=', u'>=', u'<<', u'>>', u'/', u'%', u'++', u'--', u'~', u'!', u'->'])
    lexStateNames: List[unicode] = array(java.lang.String, [u'DEFAULT', u'ASMBLOCK', u'LINEBLOCK', u'PRAGMALINE', u'OBJC', u'OBJC2'])
    tokenImage: List[unicode] = array(java.lang.String, [u'<EOF>', u'"\\ufeff"', u'" "', u'"\\f"', u'"\\t"', u'"\\n"', u'"\\r"', u'"\\\\"', u'<token of kind 8>', u'<token of kind 9>', u'<INTEGER_LITERAL>', u'<DECIMAL_LITERAL>', u'<HEX_LITERAL>', u'<OCTAL_LITERAL>', u'<FLOATING_POINT_LITERAL>', u'<EXPONENT>', u'<CHARACTER_LITERAL>', u'<STRING_LITERAL>', u'"continue"', u'<VOLATILE>', u'"register"', u'"unsigned"', u'"typedef"', u'"default"', u'"double"', u'"sizeof"', u'"switch"', u'"return"', u'"extern"', u'"\\"C\\""', u'"struct"', u'"static"', u'"_Thread_local"', u'<SIGNED>', u'"while"', u'"break"', u'"union"', u'<CONST>', u'<CDECL>', u'"__declspec"', u'<PRAGMA>', u'"__readableTo"', u'<STDCALL>', u'<FASTCALL>', u'"_Noreturn"', u'"_Alignas"', u'"_Alignof"', u'"__unaligned"', u'"__packed"', u'<ATTRIBUTE>', u'<EXTENSION>', u'<RESTRICT>', u'<ASM>', u'<INLINE>', u'<STATICASSERT>', u'"float"', u'"short"', u'"else"', u'"case"', u'"long"', u'"__int8"', u'"__int16"', u'"__int32"', u'"__int64"', u'"__ptr64"', u'"__ptr32"', u'"_Bool"', u'"__w64"', u'"enum"', u'"auto"', u'"void"', u'"char"', u'"goto"', u'"__near"', u'"__far"', u'"for"', u'"int"', u'"if"', u'"do"', u'"@protocol"', u'"@interface"', u'"#line"', u'<LINEALT>', u'<IDENTIFIER>', u'<LETTER>', u'<DIGIT>', u'" "', u'"\\t"', u'<ASMBLOCKB>', u'<ASMBLOCKP>', u'<ASM_SEMI>', u'" "', u'"\\f"', u'"\\t"', u'":"', u'<PATH_LITERAL>', u'<LINENUMBER_LITERAL>', u'" "', u'"\\f"', u'"\\t"', u'"\\n"', u'"\\r"', u'";"', u'<token of kind 103>', u'<token of kind 104>', u'<PIDENTIFIER>', u'<PLETTER>', u'<PDIGIT>', u'"("', u'")"', u'"-"', u'"+"', u'"*"', u'":"', u'","', u'<PINTEGER_LITERAL>', u'<PDECIMAL_LITERAL>', u'<PHEX_LITERAL>', u'<POCTAL_LITERAL>', u'<PSTRING_LITERAL>', u'" "', u'"\\f"', u'"\\t"', u'"\\n"', u'"\\r"', u'<OBJC_IGNORE>', u'<OBJC_IDENTIFIER>', u'<OBJC_LETTER>', u'<OBJC_DIGIT>', u'<OBJC_SEMI>', u'" "', u'"\\f"', u'"\\t"', u'"\\n"', u'"\\r"', u'"@private"', u'"@protected"', u'"@property"', u'"@optional"', u'"@required"', u'<OBJC2_IGNORE>', u'"@end"', u'"{"', u'"}"', u'";"', u'"("', u'")"', u'"["', u'"]"', u'","', u'":"', u'"="', u'"#"', u'"*"', u'"&"', u'"..."', u'"."', u'"+"', u'"-"', u'"*="', u'"/="', u'"%="', u'"+="', u'"-="', u'"<<="', u'">>="', u'"&="', u'"^="', u'"|="', u'"?"', u'"||"', u'"&&"', u'"|"', u'"^"', u'"=="', u'"!="', u'"<"', u'">"', u'"<="', u'">="', u'"<<"', u'">>"', u'"/"', u'"%"', u'"++"', u'"--"', u'"~"', u'"!"', u'"->"'])



    @overload
    def __init__(self, stream: ghidra.app.util.cparser.C.SimpleCharStream):
        """
        Constructor.
        """
        ...

    @overload
    def __init__(self, stream: ghidra.app.util.cparser.C.SimpleCharStream, lexState: int):
        """
        Constructor.
        """
        ...



    @overload
    def ReInit(self, stream: ghidra.app.util.cparser.C.SimpleCharStream) -> None:
        """
        Reinitialise parser.
        """
        ...

    @overload
    def ReInit(self, stream: ghidra.app.util.cparser.C.SimpleCharStream, lexState: int) -> None:
        """
        Reinitialise parser.
        """
        ...

    def SwitchTo(self, lexState: int) -> None:
        """
        Switch to specified lex state.
        """
        ...

    def equals(self, __a0: object) -> bool: ...

    def getClass(self) -> java.lang.Class: ...

    def getNextToken(self) -> ghidra.app.util.cparser.C.Token:
        """
        Get the next Token.
        """
        ...

    def hashCode(self) -> int: ...

    def notify(self) -> None: ...

    def notifyAll(self) -> None: ...

    def setDebugStream(self, ds: java.io.PrintStream) -> None:
        """
        Set debug output.
        """
        ...

    def toString(self) -> unicode: ...

    @overload
    def wait(self) -> None: ...

    @overload
    def wait(self, __a0: long) -> None: ...

    @overload
    def wait(self, __a0: long, __a1: int) -> None: ...

    @property
    def nextToken(self) -> ghidra.app.util.cparser.C.Token: ...