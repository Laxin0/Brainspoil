from __future__ import annotations
from enum import Enum
from dataclasses import dataclass

def error(msg):
    print(msg)
    exit(1)

iota_count = 0 
def iota():
    global iota_count
    return (iota_count := iota_count + 1)

class TokenType(Enum):
    KW_ARR = iota()
    KW_LET = iota()
    KW_CONST = iota()
    KW_PRINT = iota()
    KW_READ = iota()
    KW_IF = iota()
    KW_ELSE = iota()
    KW_WHILE = iota()
    KW_MACRO = iota()

    IDENT = iota()
    INTLIT = iota()
    STRLIT = iota()
    CHAR = iota()

    ASSIGN = iota()
    REF = iota()

    PLUS = iota()
    MINUS = iota()
    TIMES = iota()
    SLASH = iota()
    COMMA = iota()
    PAREN_OP = iota()
    PAREN_CL = iota()
    CURL_OP = iota()
    CURL_CL = iota()
    SQR_OP = iota()
    SQR_CL = iota()
    SEMI = iota()
    AND = iota()
    OR = iota()
    EQ = iota()
    NEQ = iota()
    NOT = iota()
    LESS = iota()
    GREATER = iota()
    LESSEQ = iota()
    GREATEREQ = iota()
    EOF = iota()


class BinOpKind(Enum):
    ADD = iota()
    SUB = iota()
    MULT = iota()
    DIV = iota()
    AND = iota()
    OR = iota()
    NEQ = iota()
    EQ = iota()
    LESS = iota()
    GREATER = iota()
    GREATEREQ = iota()
    LESSEQ = iota()


ttype_to_binop = { #TODO: maybe i can simplify this shit
    TokenType.PLUS: BinOpKind.ADD,
    TokenType.MINUS: BinOpKind.SUB,
    TokenType.TIMES: BinOpKind.MULT,
    TokenType.SLASH: BinOpKind.DIV,
    TokenType.AND: BinOpKind.AND,
    TokenType.OR: BinOpKind.OR,
    TokenType.EQ: BinOpKind.EQ,
    TokenType.NEQ: BinOpKind.NEQ,
    TokenType.GREATER: BinOpKind.GREATER,
    TokenType.LESS: BinOpKind.LESS,
    TokenType.GREATEREQ: BinOpKind.GREATEREQ,
    TokenType.LESSEQ: BinOpKind.LESSEQ

}

binop_prec = { # < > <= >= 9
    BinOpKind.ADD: 12,
    BinOpKind.SUB: 12,
    BinOpKind.MULT: 13,
    BinOpKind.DIV: 13,
    BinOpKind.GREATER: 9,
    BinOpKind.LESS: 9,
    BinOpKind.GREATEREQ: 9,
    BinOpKind.LESSEQ: 9,
    BinOpKind.EQ: 8,
    BinOpKind.NEQ: 8,
    BinOpKind.AND: 4,
    BinOpKind.OR: 3
}

keywords = {
    "arr": TokenType.KW_ARR,
    "let": TokenType.KW_LET,
    "print": TokenType.KW_PRINT,
    "read": TokenType.KW_READ,
    "if": TokenType.KW_IF,
    "else": TokenType.KW_ELSE,
    "while": TokenType.KW_WHILE,
    "macro": TokenType.KW_MACRO,
    "const": TokenType.KW_CONST
}

puncts = {
    ";": TokenType.SEMI,
    "=": TokenType.ASSIGN,
    "(": TokenType.PAREN_OP,
    ")": TokenType.PAREN_CL,
    "}": TokenType.CURL_CL,
    "{": TokenType.CURL_OP, 
    "[": TokenType.SQR_OP,
    "]": TokenType.SQR_CL,
    "!": TokenType.NOT,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.TIMES,
    "/": TokenType.SLASH,
    "&&": TokenType.AND,
    "&": TokenType.REF,
    "||": TokenType.OR,
    "==": TokenType.EQ,
    "!=": TokenType.NEQ,
    ">": TokenType.GREATER,
    "<": TokenType.LESS,
    ">=": TokenType.GREATEREQ,
    "<=": TokenType.LESSEQ,
    ",": TokenType.COMMA,
}

tok_to_str = {
    TokenType.KW_ARR: '`arr` keyword',
    TokenType.KW_LET: '`let` keyword',
    TokenType.KW_CONST: '`const` keyword',
    TokenType.KW_PRINT: '`print` keyword',
    TokenType.KW_READ: '`read` keyword',
    TokenType.KW_IF: '`if` keyword',
    TokenType.KW_ELSE: '`else` keyword',
    TokenType.KW_WHILE: '`while` keyword',
    TokenType.KW_MACRO: '`macro` keyword',

    TokenType.IDENT: 'identifier',
    TokenType.INTLIT: 'integer literal',
    TokenType.STRLIT: 'string literal',
    TokenType.CHAR: 'character constant',

    TokenType.ASSIGN: '`=`',
    TokenType.REF: '`&`',

    TokenType.PLUS: '`+`',
    TokenType.MINUS: '`-`',
    TokenType.TIMES: '`*`',
    TokenType.SLASH: '`/`',
    TokenType.COMMA: '`,`',
    TokenType.PAREN_OP: '`(`',
    TokenType.PAREN_CL: '`)`',
    TokenType.CURL_OP: '`{`',
    TokenType.CURL_CL: '`}`',
    TokenType.SQR_CL: '`]`',
    TokenType.SQR_OP: '`[`',
    TokenType.SEMI: '`;`',
    TokenType.AND: '`&&`',
    TokenType.OR: '`||`',
    TokenType.EQ: '`==`',
    TokenType.NEQ: '`!=`',
    TokenType.NOT: '`!`',
    TokenType.LESSEQ: '`<=`',
    TokenType.LESS: '`<`',
    TokenType.GREATER: '`>`',
    TokenType.GREATEREQ: '`>=`',

    TokenType.EOF: 'end of file',
}

esc_chars = { #TODO: add more
    'n': '\n',
    't': '\t',
    '0': '\0',
    'r': '\r',
    '"': '\"'
}

@dataclass
class Token():
    type: TokenType
    val: str|int|None
    loc: str



###########################################################################################################
#                                                                                                         #
#                                            AST NODES                                                    #
#                                                                                                         #
###########################################################################################################

@dataclass
class Arg():
    val: NTerm
    is_ref: bool

@dataclass
class Expr(): pass #TODO add loc field for NBinExpr and NTerm ???

@dataclass
class NNot():
    expr: NTerm

@dataclass
class NTerm(Expr):
    val: Token|NMacroUse|NNot|NIndex

@dataclass
class NBinExpr(Expr):
    lhs: Expr
    rhs: Expr
    op: BinOpKind

@dataclass
class Statement(): pass

@dataclass 
class NStr(Statement):
    string: str

@dataclass
class NScope(Statement):
    stmts: list[Statement]

@dataclass
class NDeclare(Statement):
    id: Token
    val: Expr

@dataclass 
class NConstDecl(Statement):
    id: Token
    val: int

@dataclass
class NArrDecl(Statement):
    id: Token
    size: Token

@dataclass
class NAssign(Statement):
    lhs: Token | NIndex
    rhs: Expr

@dataclass
class NPrint(Statement):
    expr: Expr

@dataclass
class NRead(Statement):
    id: Token

@dataclass
class NIfElse(Statement):
    cond: Expr
    then: NScope
    elze: NScope

@dataclass
class NWhile(Statement):
    cond: Expr
    body: NScope

@dataclass
class NMacroDef(Statement):
    is_func: bool
    name: Token
    args: list[Token]
    body: NScope

@dataclass
class NMacroUse():
    name: Token
    args: list[Expr]

@dataclass
class NIndex():
    arr_id: Token
    index: Expr

@dataclass
class VarData():
    addr: int

@dataclass
class ArrData():
    addr: int

@dataclass
class ConstData():
    val: int

@dataclass
class NProg():
    stmts: list[Statement]