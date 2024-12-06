class Lexer():
    def __init__(self, src):
        self.src = src
        self.index = 0

    def next(self):
        if self.index >= len(self.src): return None
        
        c = self.src[self.index]
        self.index += 1
        return c
    
    # if found exp then Returns Ok(exp) and changes index
    # else              Returns Err() and don't changes index
    def exp(self, expected):
        t = self.index

        res = self.next()
        if res == expected:
            return res
        
        self.index = t
        return None

#  Grammar
#
#  C ::= A | B
#  D ::= A B
#  A ::= a
#  B ::= b
#  M ::= C M | C      OR     M ::= [C]     *At least one element*

def parseA(lex):
    return lex.exp('a')

def parseB(lex):
    return lex.exp('b')

def parseC(lex):
    return parseA(lex) or parseB(lex)

def parseD(lex):
    a = parseA(lex)
    b = parseB(lex)
    a2 = parseA(lex)

    if not all((a, b, a2)):
        return None
    
    return a+b+a2

def rparseM(lex):
    c = parseC(lex)
    if not c: return None
    m = rparseM(lex)
    if not m: return c
    return c+m

def iparseM(lex):
    cs = []
    while c := parseC(lex):
        cs.append(c)

    return "".join(cs) if len(cs) > 0 else None


def main():
    l = Lexer("abab")
    print(parseC(l), parseC(l), parseD(l))
    l = Lexer("aaaaa")
    print(iparseM(l))

main()
