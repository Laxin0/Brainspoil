from enum import Enum

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

class Loc():
    def __init__(self, path, line, col):
        self.path = path
        self.line = line
        self.col = col
    
    def __str__(self):
        return f"{self.path}:{self.line}:{self.col}"

class Token():
    def __init__(self, ttype: TokenType, val: str|int|None, loc: Loc) -> None:
        self.type = ttype
        self.val = val
        self.loc = loc

class Lexer():
    def __init__(self, src, path):
        self.src = src
        self.path = path
        self.index = 0
        self.line = 1
        self.col = 1

    def next():
        pass