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
    KW_LET = iota()
    KW_PRINT = iota()
    KW_READ = iota()
    KW_IF = iota()
    KW_ELSE = iota()
    KW_WHILE = iota()

    IDENT = iota()
    INTLIT = iota()

    ASSIGN = iota()

    BINOP = iota()
    PAREN_OP = iota()
    PAREN_CL = iota()
    CURL_OP = iota()
    CURL_CL = iota()
    SEMI = iota()
    AND = iota()

    EOF = iota()


class BinOpKind(Enum):
    ADD = iota()
    SUB = iota()
    MULT = iota()
    DIV = iota()

str_to_binop = {
    '+': BinOpKind.ADD,
    '-': BinOpKind.SUB,
    '*': BinOpKind.MULT,
    '/': BinOpKind.DIV
}

binop_prec = {
    BinOpKind.ADD: 1,
    BinOpKind.SUB: 1,
    BinOpKind.MULT: 2,
    BinOpKind.DIV: 2,
}

keywords = {
    "let": TokenType.KW_LET,
    "print": TokenType.KW_PRINT,
    "read": TokenType.KW_READ,
    "if": TokenType.KW_IF,
    "else": TokenType.KW_ELSE,
    "while": TokenType.KW_WHILE
}

puncts = {
    ";": TokenType.SEMI,
    "=": TokenType.ASSIGN,
    "(": TokenType.PAREN_OP,
    ")": TokenType.PAREN_CL,
    "}": TokenType.CURL_CL,
    "{": TokenType.CURL_OP,
    "&": TokenType.AND
}

tok_to_str = {
    TokenType.KW_LET: '`let` keyword',
    TokenType.KW_PRINT: '`print` keyword',
    TokenType.KW_READ: '`read` keyword',
    TokenType.KW_IF: '`if` keyword',
    TokenType.KW_ELSE: '`else` keyword',
    TokenType.KW_WHILE: '`while` keyword',

    TokenType.IDENT: 'identifier',
    TokenType.INTLIT: 'integer literal',

    TokenType.ASSIGN: '`=`',

    TokenType.BINOP: '`+`, `-`, `*` or `/`',
    TokenType.PAREN_OP: '`(`',
    TokenType.PAREN_CL: '`)`',
    TokenType.CURL_OP: '`{`',
    TokenType.CURL_CL: '`}`',
    TokenType.SEMI: '`;`',
    TokenType.AND: '`&`',

    TokenType.EOF: 'end of file',
}

@dataclass
class Token():
    type: TokenType
    val: str|int|None
    loc: str

    # def __str__(self):
    #     return f"{self.type.name}({self.val}) at {self.loc}"


###########################################################################################################
#                                                                                                         #
#                                            AST NODES                                                    #
#                                                                                                         #
###########################################################################################################

@dataclass
class Expr(): pass

@dataclass
class NDeref():
    expr: Expr

@dataclass
class NTerm(Expr):
    val: Token|int|NDeref

@dataclass
class NBinExpr(Expr):
    lhs: Expr
    rhs: Expr
    op: BinOpKind

@dataclass
class Statement(): pass

@dataclass
class NScope(Statement):
    stmts: list[Statement]

@dataclass
class NDeclare(Statement):
    id: Token
    val: Expr

@dataclass
class NAssign(Statement):
    id: Token
    val: Expr

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
class NProg():
    stmts: list[Statement]