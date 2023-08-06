from typing import List
import ghidra.app.util.cparser.CPP
import ghidra.app.util.cparser.CPP.PreProcessor
import ghidra.util.task
import java.io
import java.lang


class PreProcessor(object, ghidra.app.util.cparser.CPP.PreProcessorConstants):
    AND: int = 105
    BEGITEM: int = 122
    CMNTNL: int = 9
    CMT: int = 31
    COD: int = 35
    COLON: int = 118
    COMMA: int = 85
    COMMENT: int = 21
    CONLINE: int = 176
    CONSTANT: int = 19
    CONSTITUENT: int = 168
    CONTARG: int = 28
    CP: int = 42
    DECIMAL_LITERAL: int = 60
    DEFAULT: int = 0
    DEFD: int = 39
    DEFINE: int = 18
    DEFINED: int = 95
    DIR: int = 29
    DIRECTIVE: int = 3
    DIRECTIVECOMMENT: int = 23
    DIRLINE: int = 124
    DIVIDE: int = 114
    ECMT: int = 32
    ELIF: int = 89
    ELSE: int = 90
    ENDCMT: int = 33
    ENDIF: int = 91
    ENDITEM: int = 123
    ENDL: int = 36
    ENDREL: int = 41
    EOF: int = 0
    EOLCMNTNL: int = 7
    EQ: int = 99
    ERRLINE: int = 159
    ERROR: int = 14
    ERROR_EXPRN: int = 158
    ESTD: int = 143
    EXPATH: int = 135
    EXPONENT: int = 65
    FP_LITERAL: int = 64
    FP_NUMERIC: int = 120
    GE: int = 104
    GT: int = 102
    HASINCLUDE: int = 96
    HASINCLUDENEXT: int = 97
    HEX_DIGIT: int = 62
    HEX_LITERAL: int = 61
    IF: int = 88
    IFDEF: int = 12
    IFDEFED: int = 92
    IFDEF_EXPRN: int = 150
    IFDLINE: int = 151
    IFNDEF: int = 13
    IFNDEFED: int = 93
    IFNDEF_EXPRN: int = 154
    IFNDLINE: int = 155
    IGNORETOEOL: int = 4
    INCDEF: int = 5
    INCLINE: int = 137
    INCLUDE: int = 8
    INFO: int = 16
    INFOLINE: int = 165
    INFO_EXPRN: int = 164
    INTEGER_LITERAL: int = 59
    ITEM: int = 121
    LE: int = 103
    LEADIN3: int = 212
    LINE: int = 20
    LINECOMMENT: int = 22
    LINEINFO: int = 178
    LINLINE: int = 177
    LOG_AND: int = 109
    LOG_OR: int = 108
    LSH: int = 110
    LT: int = 101
    MACEXPPATH: int = 138
    MACROARGS: int = 27
    MACROARGSEND: int = 197
    MACROMV: int = 195
    MACROMVTAG: int = 196
    MACRORV: int = 205
    MACRORVCMT: int = 206
    MACROVALS: int = 29
    MACROVALS_COMMENT: int = 31
    MANIFEST: int = 175
    MCVLINE: int = 211
    MINUS: int = 112
    MOD: int = 115
    MOREARG: int = 204
    MOREVAL: int = 190
    MQUOTED_VAL: int = 30
    MQUOTED_VALUE: int = 214
    NEQ: int = 100
    NEWLINE: int = 69
    NOPAR: int = 44
    NOT: int = 94
    NOTCHR: int = 66
    NOTCMT: int = 51
    NOTCMTCOD: int = 52
    NOTENDL: int = 48
    NOTENDLC: int = 49
    NOTENDLSTAR: int = 50
    NOTVALCMT: int = 58
    NOTWQC: int = 55
    NOTWS: int = 53
    NOTWSQ: int = 54
    NOTWSQLT: int = 57
    NOTWWSQLT: int = 56
    NUMERIC: int = 119
    OCTAL_LITERAL: int = 63
    OP: int = 43
    OPTD: int = 40
    OPTIONED: int = 98
    OR: int = 106
    OTHER_TEXT: int = 70
    OUTER_TEXT: int = 68
    PLUS: int = 113
    PRAGMA: int = 11
    PRAGMA_EXPRN: int = 147
    PRGLINE: int = 148
    QMARK: int = 117
    QUOTED_TEXT: int = 71
    QUOTED_VAL: int = 26
    QUOTED_VALUE: int = 194
    REL: int = 47
    RELATIVE: int = 146
    RELPATH: int = 10
    RSH: int = 111
    RVALUES: int = 24
    RVALUES_COMMENT: int = 25
    RVSLINE: int = 187
    STANDARD: int = 144
    STARTCMT: int = 34
    STD: int = 46
    STDPATH: int = 9
    SpecialBlockComment: int = 2
    SpecialEOLComment: int = 1
    TIMES: int = 116
    UNDEFINE: int = 17
    UNDIR: int = 37
    UNDIRALL: int = 38
    UNDLINE: int = 169
    VALUES: int = 188
    VALUESCMT: int = 189
    WARNING: int = 15
    WARNING_EXPRN: int = 161
    WARNLINE: int = 162
    WS: int = 67
    WSP: int = 45
    XOR: int = 107
    XSYM: int = 30
    XSYMLINK: int = 6
    XSYMLINKPATH: int = 136
    XSYMPATH: int = 7
    _AND: int = 17
    _BLANKLINE: int = 4
    _BOM: int = 1
    _CMT: int = 6
    _CMT0: int = 87
    _CMT11: int = 127
    _CMT3: int = 180
    _CMT4: int = 183
    _CMT5: int = 199
    _COD: int = 139
    _COD1: int = 83
    _COD2: int = 186
    _COD3: int = 201
    _COD4: int = 208
    _CODC: int = 174
    _COLON: int = 28
    _CTRL: int = 2
    _ECMT10: int = 181
    _ECMT3: int = 179
    _ECMT5: int = 198
    _ECMT7: int = 191
    _ECMT8: int = 209
    _ECMT9: int = 215
    _EECMT7: int = 192
    _EECMT9: int = 217
    _EEECMT9: int = 216
    _ENDREL: int = 145
    _EQ: int = 11
    _EQT: int = 193
    _EQT1: int = 213
    _GE: int = 16
    _GT: int = 14
    _HEX: int = 133
    _INCCOD: int = 128
    _INCCP: int = 130
    _INCOP: int = 131
    _INCSTANDARD: int = 132
    _INCWSP: int = 129
    _LCMT: int = 5
    _LCMT0: int = 86
    _LCMT11: int = 126
    _LCMT20: int = 152
    _LCMT21: int = 156
    _LCMT4: int = 182
    _LCMT7: int = 207
    _LE: int = 15
    _LEADIN1: int = 167
    _LEADIN2: int = 170
    _LOG_AND: int = 18
    _LOG_OR: int = 21
    _LSH: int = 22
    _LT: int = 13
    _MACWSP: int = 202
    _MINUS: int = 24
    _MWSP: int = 200
    _NEQ: int = 12
    _OR: int = 19
    _PERCENT: int = 25
    _PLUS: int = 26
    _QMARK: int = 27
    _QTE: int = 142
    _QTE0: int = 184
    _QTE1: int = 210
    _RSH: int = 23
    _TOEOL: int = 125
    _WSP: int = 140
    _WSP0: int = 82
    _WSP1: int = 149
    _WSP2: int = 84
    _WSP3: int = 153
    _WSP4: int = 157
    _WSP5: int = 160
    _WSP6: int = 163
    _WSP7: int = 173
    _WSP8: int = 185
    _WSP_INFO: int = 166
    _XOR: int = 20
    _XSYM: int = 3
    _XSYMENDL: int = 134
    __LT: int = 141
    jj_nt: ghidra.app.util.cparser.CPP.Token
    token: ghidra.app.util.cparser.CPP.Token
    tokenImage: List[unicode] = array(java.lang.String, [u'<EOF>', u'"\\ufeff"', u'<_CTRL>', u'<_XSYM>', u'<_BLANKLINE>', u'<_LCMT>', u'<_CMT>', u'<EOLCMNTNL>', u'<token of kind 8>', u'<CMNTNL>', u'<token of kind 10>', u'"=="', u'"!="', u'"<"', u'">"', u'"<="', u'">="', u'"&"', u'"&&"', u'"|"', u'"^"', u'"||"', u'"<<"', u'">>"', u'"-"', u'"%"', u'"+"', u'"?"', u'":"', u'"#"', u'"XSym"', u'"/"', u'"*"', u'"*/"', u'"/*"', u'<COD>', u'<ENDL>', u'<UNDIR>', u'<UNDIRALL>', u'"defined"', u'"__option"', u'"\\""', u'")"', u'"("', u'<NOPAR>', u'<WSP>', u'<STD>', u'<REL>', u'<NOTENDL>', u'<NOTENDLC>', u'<NOTENDLSTAR>', u'<NOTCMT>', u'<NOTCMTCOD>', u'<NOTWS>', u'<NOTWSQ>', u'<NOTWQC>', u'<NOTWWSQLT>', u'<NOTWSQLT>', u'"/##/"', u'<INTEGER_LITERAL>', u'<DECIMAL_LITERAL>', u'<HEX_LITERAL>', u'<HEX_DIGIT>', u'<OCTAL_LITERAL>', u'<FP_LITERAL>', u'<EXPONENT>', u'"!"', u'<WS>', u'<OUTER_TEXT>', u'<NEWLINE>', u'<OTHER_TEXT>', u'<QUOTED_TEXT>', u'"include"', u'"import"', u'"include_next"', u'"pragma"', u'"error"', u'"warning"', u'"info"', u'"define"', u'"undef"', u'"line"', u'<_WSP0>', u'<_COD1>', u'<_WSP2>', u'","', u'<_LCMT0>', u'<_CMT0>', u'"if"', u'"elif"', u'"else"', u'"endif"', u'"ifdef"', u'"ifndef"', u'<NOT>', u'<DEFINED>', u'"__has_include"', u'"__has_include_next"', u'<OPTIONED>', u'<EQ>', u'<NEQ>', u'<LT>', u'<GT>', u'<LE>', u'<GE>', u'<AND>', u'<OR>', u'<XOR>', u'<LOG_OR>', u'<LOG_AND>', u'<LSH>', u'<RSH>', u'<MINUS>', u'<PLUS>', u'<DIVIDE>', u'<MOD>', u'<TIMES>', u'<QMARK>', u'<COLON>', u'<NUMERIC>', u'<FP_NUMERIC>', u'<ITEM>', u'<BEGITEM>', u'<ENDITEM>', u'<DIRLINE>', u'<_TOEOL>', u'<_LCMT11>', u'<_CMT11>', u'<_INCCOD>', u'<_INCWSP>', u'<_INCCP>', u'<_INCOP>', u'<_INCSTANDARD>', u'<_HEX>', u'<_XSYMENDL>', u'<EXPATH>', u'<XSYMLINKPATH>', u'<INCLINE>', u'<MACEXPPATH>', u'<_COD>', u'<_WSP>', u'<__LT>', u'<_QTE>', u'<ESTD>', u'<STANDARD>', u'<_ENDREL>', u'<RELATIVE>', u'<PRAGMA_EXPRN>', u'<PRGLINE>', u'<_WSP1>', u'<IFDEF_EXPRN>', u'<IFDLINE>', u'<_LCMT20>', u'<_WSP3>', u'<IFNDEF_EXPRN>', u'<IFNDLINE>', u'<_LCMT21>', u'<_WSP4>', u'<ERROR_EXPRN>', u'<ERRLINE>', u'<_WSP5>', u'<WARNING_EXPRN>', u'<WARNLINE>', u'<_WSP6>', u'<INFO_EXPRN>', u'<INFOLINE>', u'<_WSP_INFO>', u'<_LEADIN1>', u'<CONSTITUENT>', u'<UNDLINE>', u'<_LEADIN2>', u'"("', u'")"', u'<_WSP7>', u'<_CODC>', u'<MANIFEST>', u'<CONLINE>', u'<LINLINE>', u'<LINEINFO>', u'<_ECMT3>', u'<_CMT3>', u'<_ECMT10>', u'<_LCMT4>', u'<_CMT4>', u'<_QTE0>', u'<_WSP8>', u'<_COD2>', u'<RVSLINE>', u'<VALUES>', u'<VALUESCMT>', u'<MOREVAL>', u'<_ECMT7>', u'<_EECMT7>', u'<_EQT>', u'<QUOTED_VALUE>', u'<MACROMV>', u'<MACROMVTAG>', u'")"', u'<_ECMT5>', u'<_CMT5>', u'","', u'<_COD3>', u'<_MACWSP>', u'")"', u'<MOREARG>', u'<MACRORV>', u'<MACRORVCMT>', u'<_LCMT7>', u'<_COD4>', u'<_ECMT8>', u'<_QTE1>', u'<MCVLINE>', u'<LEADIN3>', u'<_EQT1>', u'<MQUOTED_VALUE>', u'<_ECMT9>', u'<_EEECMT9>', u'<_EECMT9>'])
    token_source: ghidra.app.util.cparser.CPP.PreProcessorTokenManager



    @overload
    def __init__(self): ...

    @overload
    def __init__(self, filename: unicode): ...

    @overload
    def __init__(self, args: List[unicode]): ...

    @overload
    def __init__(self, tm: ghidra.app.util.cparser.CPP.PreProcessorTokenManager):
        """
        Constructor with generated Token Manager.
        """
        ...

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



    def ANDExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def AdditiveExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def Assertion(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def CompoundAndExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def CompoundConditionalExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def CompoundOrExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def ConditionalExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def ControlLine(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def Define(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def ElIf(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def Else(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def ElseIfCondition(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def ElseMark(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def EndIf(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def EqualTo(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def EqualityExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def Error(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def ExclusiveORExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def Expression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def GreaterThan(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def GreaterThanExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def GreaterThanOrEqual(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def GreaterThanOrEqualExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def Group(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def GroupPart(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def IFGroup(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def IFSection(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def If(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def IfCondition(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def IfDef(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def IfDefExpr(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def IfNDef(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def IfNDefExpr(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def InEqualityExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def Include(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def InclusiveORExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def Info(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def Input(self) -> None: ...

    def LessExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def LessThan(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def LessThanOrEqual(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def LessThanOrEqualExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def LineInfo(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def LogAnd(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def LogNegation(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def LogOr(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def LogicalAndExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def LogicalOrExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def MacroArgs(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def MacroVals(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def MultiplicativeExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def NewLines(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def NoMas(self) -> None: ...

    def NotEqualTo(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def Pragma(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def Qmark(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def QuotedText(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def QuotedValue(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    @overload
    def ReInit(self, tm: ghidra.app.util.cparser.CPP.PreProcessorTokenManager) -> None:
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

    def RelationalExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def ShiftExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def Text(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def TranslationUnit(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def UnDef(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def UnaryExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def ValueExpression(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def Values(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def Warning(self) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def addIncludePath(self, path: unicode) -> None: ...

    def addIncludePaths(self, paths: List[unicode]) -> None: ...

    def curFileStackTop(self) -> unicode: ...

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

    def generateParseException(self) -> ghidra.app.util.cparser.CPP.ParseException:
        """
        Generate ParseException.
        """
        ...

    def getClass(self) -> java.lang.Class: ...

    @overload
    def getDef(self, name: unicode) -> unicode: ...

    @overload
    def getDef(self, def_: ghidra.app.util.cparser.CPP.PreProcessor.PPToken) -> ghidra.app.util.cparser.CPP.PreProcessor.PPToken: ...

    def getDefinitions(self) -> ghidra.app.util.cparser.CPP.DefineTable: ...

    def getDoubleValue(self, val: unicode) -> float: ...

    def getNextToken(self) -> ghidra.app.util.cparser.CPP.Token:
        """
        Get the next Token.
        """
        ...

    def getNumericType(self, val: unicode) -> int: ...

    def getParseMessages(self) -> unicode: ...

    def getToken(self, index: int) -> ghidra.app.util.cparser.CPP.Token:
        """
        Get the specific Token.
        """
        ...

    def hashCode(self) -> int: ...

    def isArg(self, arg: ghidra.app.util.cparser.CPP.PreProcessor.PPToken) -> bool: ...

    def isDef(self, def_: ghidra.app.util.cparser.CPP.PreProcessor.PPToken) -> bool: ...

    @staticmethod
    def main(args: List[unicode]) -> None: ...

    def notify(self) -> None: ...

    def notifyAll(self) -> None: ...

    def parse(self, filename: unicode) -> bool: ...

    def setArgs(self, args: List[unicode]) -> None: ...

    def setMonitor(self, monitor: ghidra.util.task.TaskMonitor) -> None: ...

    def setOutputStream(self, fos: java.io.OutputStream) -> None: ...

    def toString(self) -> unicode: ...

    def verboseLevel(self) -> int: ...

    @overload
    def wait(self) -> None: ...

    @overload
    def wait(self, __a0: long) -> None: ...

    @overload
    def wait(self, __a0: long, __a1: int) -> None: ...

    @property
    def args(self) -> None: ...  # No getter available.

    @args.setter
    def args(self, value: List[unicode]) -> None: ...

    @property
    def definitions(self) -> ghidra.app.util.cparser.CPP.DefineTable: ...

    @property
    def monitor(self) -> None: ...  # No getter available.

    @monitor.setter
    def monitor(self, value: ghidra.util.task.TaskMonitor) -> None: ...

    @property
    def nextToken(self) -> ghidra.app.util.cparser.CPP.Token: ...

    @property
    def outputStream(self) -> None: ...  # No getter available.

    @outputStream.setter
    def outputStream(self, value: java.io.OutputStream) -> None: ...

    @property
    def parseMessages(self) -> unicode: ...