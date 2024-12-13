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

    IDENT = iota()
    INTLIT = iota()

    ASSIGN = iota()

    BINOP = iota()
    PAREN_OP = iota()
    PAREN_CL = iota()
    SEMI = iota()

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
    "let": TokenType.KW_LET
}

puncts = {
    ";": TokenType.SEMI,
    "=": TokenType.ASSIGN,
    "(": TokenType.PAREN_OP,
    ")": TokenType.PAREN_CL
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
class NTerm(Expr):
    val: Token|int

@dataclass
class NBinExpr(Expr):
    lhs: Expr
    rhs: Expr
    op: BinOpKind

@dataclass
class Statement(): pass

@dataclass
class NDeclare(Statement):
    id: Token
    val: Expr

@dataclass
class NProg():
    stmts: list[Statement]