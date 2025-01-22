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
    CHAR = iota()

    ASSIGN = iota()

    PLUS = iota()
    MINUS = iota()
    TIMES = iota()
    SLASH = iota()
    PAREN_OP = iota()
    PAREN_CL = iota()
    CURL_OP = iota()
    CURL_CL = iota()
    SEMI = iota()
    AND = iota()
    OR = iota()
    AT = iota()
    NOT = iota()

    EOF = iota()


class BinOpKind(Enum):
    ADD = iota()
    SUB = iota()
    MULT = iota()
    DIV = iota()
    AND = iota()
    OR = iota()

ttype_to_binop = {
    TokenType.PLUS: BinOpKind.ADD,
    TokenType.MINUS: BinOpKind.SUB,
    TokenType.TIMES: BinOpKind.MULT,
    TokenType.SLASH: BinOpKind.DIV,
    TokenType.AND: BinOpKind.AND,
    TokenType.OR: BinOpKind.OR
}

binop_prec = {
    BinOpKind.ADD: 3,
    BinOpKind.SUB: 3,
    BinOpKind.MULT: 4,
    BinOpKind.DIV: 4,
    BinOpKind.AND: 2,
    BinOpKind.OR: 1
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
    "@": TokenType.AT,
    "!": TokenType.NOT,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.TIMES,
    "/": TokenType.SLASH
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
    TokenType.CHAR: 'character constant',

    TokenType.ASSIGN: '`=`',

    TokenType.PLUS: '`+`',
    TokenType.MINUS: '`-`',
    TokenType.TIMES: '`*`',
    TokenType.SLASH: '`/`',
    TokenType.PAREN_OP: '`(`',
    TokenType.PAREN_CL: '`)`',
    TokenType.CURL_OP: '`{`',
    TokenType.CURL_CL: '`}`',
    TokenType.SEMI: '`;`',
    TokenType.AND: '`&`',
    TokenType.AT: '`@`',
    TokenType.NOT: '`!`',

    TokenType.EOF: 'end of file',
}

esc_chars = { #TODO: add more or use more elegant algorithm
    'n': '\n',
    't': '\t',
    '0': '\0',
    'r': '\r'
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
class NLoad():
    addr: Expr

@dataclass
class NNot():
    expr: NTerm

@dataclass
class NTerm(Expr):
    val: Token|int|NLoad

@dataclass
class NBinExpr(Expr):
    lhs: Expr
    rhs: Expr
    op: BinOpKind

@dataclass
class Statement(): pass

@dataclass
class NStore(Statement):
    addr: Expr
    val: Expr

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