from enum import Enum
from dataclasses import dataclass

iota_count = 0 
def iota():
    global iota_count
    return (iota_count := iota_count + 1)

class TokenType(Enum):
    KW_LET = iota()

    IDENT = iota()
    INTLIT = iota()

    ASSIGN = iota()
    SEMI = iota()

    EOF = iota()

class BinOpKind(Enum):
    ADD = iota()
    SUB = iota()

keywords = {
    "let": TokenType.KW_LET
}

puncts = {
    ";": TokenType.SEMI,
    "=": TokenType.ASSIGN
}

@dataclass
class Token():
    type: TokenType
    val: str|int|None
    loc: str

    # def __str__(self):
    #     return f"{self.type.name}({self.val}) at {self.loc}"

class Lexer():
    def __init__(self, src, path):
        self.src = src
        self.path = path
        self.index = 0
        self.line = 1
        self.col = 1
        self.buffer = self.next()

    def loc(self):
        return f"{self.path}:{self.line}:{self.col}"

    def next(self):
        c: str
        while True:
            if self.index >= len(self.src): return Token(TokenType.EOF, None, self.loc())
            c = self.src[self.index]

            if c == '\n':
                self.index += 1
                self.col = 1
                self.line +=1

            elif c.isspace():
                self.index += 1
                self.col += 1

            elif c.isalpha():
                loc = self.loc()
                buff = ""
                while c.isalnum():
                    buff += c
                    self.index += 1
                    self.col += 1
                    if self.index >= len(self.src): return Token(TokenType.EOF, None, self.loc())
                    c = self.src[self.index]
                if buff in keywords.keys():
                    return Token(keywords[buff], None, loc)
                else:
                    return Token(TokenType.IDENT, buff, loc)
                
            elif c.isnumeric():
                loc = self.loc()
                buff = ""
                while c.isnumeric():
                    buff += c
                    self.index += 1
                    self.col += 1
                    if self.index >= len(self.src): return Token(TokenType.EOF, None, self.loc())
                    c = self.src[self.index]
                return Token(TokenType.INTLIT, buff, loc)
            
            elif c in puncts.keys():
                loc = self.loc()
                self.index += 1
                self.col += 1
                return Token(puncts[c], None, loc)
            
            else:
                print(f"{self.loc()}: ERROR: Invalid character `{c}`")
                exit(1)

    def peek(self, ttype: TokenType):
        return self.buffer.type == ttype

    def expect(self, ttype: TokenType):
        if self.buffer.type == ttype:
            t = self.buffer
            self.buffer = self.next()
            return t
        else:
            print(f"{self.loc()}: ERROR: Expected `{ttype}` but found `{self.buffer}`")
            exit(1)

@dataclass
class NExpr(): pass

@dataclass
class NTerm(NExpr):
    val: Token|int

@dataclass
class NBinExpr(NExpr):
    lhs: NExpr
    rhs: NExpr
    op: BinOpKind

@dataclass
class NDeclare():
    id: Token
    val: NExpr


def expr(lex: Lexer):
    if lex.peek(TokenType.INTLIT):
        return NTerm(int(lex.expect(TokenType.INTLIT).val))
    elif lex.peek(TokenType.IDENT):
        return NTerm(lex.expect(TokenType.IDENT).val)
    print(f"{lex.peek().loc}: ERROR: Expected ident or intlit but found `{lex.peek()}`")
    exit(1)

def declare(lex: Lexer):
    _ = lex.expect(TokenType.KW_LET)
    id = lex.expect(TokenType.IDENT)
    if lex.peek(TokenType.ASSIGN):
        _ = lex.expect(TokenType.ASSIGN)
        exp = expr(lex)
        _ = lex.expect(TokenType.SEMI)
        return NDeclare(id, exp)
    elif lex.peek(TokenType.SEMI):
        _ = lex.expect(TokenType.SEMI)
        return NDeclare(id, NTerm(0))
    print(f"{lex.peek().loc}: ERROR: Expected `=` or `;` but found `{lex.peek()}`")
    exit(1)

head = 0
sp = 0
bfvars = {}
bf_code = ""

def to(addr):
    global head, sp
    steps = addr-head
    head = addr
    if steps < 0:
        steps *= -1
        return '<'*steps
    else:
        return '>'*steps

def store(addr: int):
    global sp
    res = f"{to(addr)}[-]{to(sp-1)}[-{to(addr)}+{to(sp-1)}]"
    sp -= 1
    return res

def top(addr: int):
    global sp
    res = f"{to(addr)}[-{to(sp)}+>+{to(addr)}]{to(sp+1)}[-{to(addr)}+{to(sp+1)}]"
    sp += 1
    return res

def pushint(n: int):
    global sp
    res = to(sp) + '[-]' + '+'*n
    sp += 1
    return res

def gen_term(node: NTerm):
    assert isinstance(node, NTerm)
    val = node.val
    if isinstance(val, Token):
        assert val.type == TokenType.IDENT
        if not (val.val in bfvars.keys()):
            print(f"{val.loc}: ERROR: Vriable `{val.val}` not declared.")
            exit(1)
        return top(bfvars[val.val])
    elif isinstance(val, int):
        return pushint(val)


def gen_expr(node: NExpr):
    if isinstance(node, NTerm):
        return gen_term(node)
    elif isinstance(node, NBinExpr):
        print("Not implemented")
        assert False
    else:
        assert False #Unreacheable

def gen_declare(node: NDeclare):
    global bfvars, sp
    assert isinstance(node, NDeclare)
    id, exp = node.id, node.val
    if id.val in bfvars.keys():
        print(f"{id.loc}: ERROR: Variable `{id.val}` already declared.")
        exit(1)
    addr = sp
    bfvars.update({id.val: addr})
    sp += 1
    return gen_expr(exp) + store(addr)



def main():
    src = ''
    with open("code.bs") as f:
        src = f.read()
    l = Lexer(src, "code.bs")
    print(gen_declare(declare(l)))
    print(gen_declare(declare(l)))

if __name__ == "__main__":
    main()
