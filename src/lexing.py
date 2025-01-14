from definitions import *

class Lexer():
    def __init__(self, src, path):
        self.src = src
        self.path = path
        self.index = 0
        self.line = 1
        self.col = 1
        self.buffer = self.next()

    def loc(self) -> str:
        return f"{self.path}:{self.line}:{self.col}"

    def next(self) -> Token:
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
            
            elif c in str_to_binop.keys():
                loc = self.loc()
                self.index += 1
                self.col += 1
                return Token(TokenType.BINOP, str_to_binop[c], loc)
            elif c == '#':
                while c != '\n':
                    self.index += 1
                    if self.index >= len(self.src):
                        return Token(TokenType.EOF, None, self.loc())
                    c = self.src[self.index]
                self.col = 1
                self.line += 1
            elif c == '\'':
                loc = self.loc()
                self.index += 1; self.col += 1
                char = ''
                current = self.src[self.index]
                if current == '\\':
                    self.index += 1; self.col += 1
                    if self.src[self.index] == '\n': error(f"{self.loc()}: ERROR: Character constant must be in the one line.")
                    if not(self.src[self.index] in esc_chars.keys()): error(f"{self.loc()}: ERROR: Unknown escape character `{self.src[self.index]}`")
                    char = esc_chars[self.src[self.index]]
                elif current == '\n': error(f"{self.loc()}: ERROR: Character constant must be in the one line.")
                else:
                    char = current
                self.index += 1; self.col += 1
                if self.src[self.index] != '\'': error(f"{self.loc()}: ERROR: Expected closing `'` in character constant, but found `{self.src[self.index]}`")
                self.index += 1; self.col += 1
                return Token(TokenType.CHAR, char, loc)
            else:
                error(f"{self.loc()}: ERROR: Invalid character `{c}`")

    def next_is(self, ttype: TokenType) -> bool:
        return self.buffer.type == ttype
    
    def peek(self) -> Token:
        return self.buffer

    def expect(self, ttype: TokenType) -> Token:
        if self.buffer.type == ttype:
            t = self.buffer
            self.buffer = self.next()
            return t
        else:
            error(f"{self.loc()}: ERROR: Expected {tok_to_str[ttype]} but found {tok_to_str[self.buffer.type]}")

def parse_term(lex: Lexer) -> Expr:
    if lex.next_is(TokenType.INTLIT):
        return NTerm(int(lex.expect(TokenType.INTLIT).val))
    elif lex.next_is(TokenType.IDENT):
        return NTerm(lex.expect(TokenType.IDENT))
    elif lex.next_is(TokenType.PAREN_OP):
        lex.expect(TokenType.PAREN_OP)
        exp = parse_expr(lex, 1)
        lex.expect(TokenType.PAREN_CL)
        return exp
    elif lex.next_is(TokenType.AND):
        lex.expect(TokenType.AND)
        exp = parse_term(lex)
        return NTerm(NLoad(exp))
    elif lex.next_is(TokenType.CHAR):
        return NTerm(ord(lex.expect(TokenType.CHAR).val))
    else:
        error(f"{lex.peek().loc}: ERROR: Expected {tok_to_str[TokenType.INTLIT]}, {tok_to_str[TokenType.IDENT]} or {tok_to_str[TokenType.PAREN_OP]} " +\
              f" but found {tok_to_str[lex.peek().type]}")


def parse_expr(lex: Lexer, min_prec) -> Expr:
    lhs = parse_term(lex)
    
    while True:
        if not lex.next_is(TokenType.BINOP) or binop_prec[lex.peek().val] < min_prec:
            break
        op = lex.expect(TokenType.BINOP).val
        prec = binop_prec[op]
        next_min_prec = prec + 1

        rhs = parse_expr(lex, next_min_prec)

        lhs = NBinExpr(lhs, rhs, op)

    return lhs


def parse_declare(lex: Lexer) -> NDeclare:
    _ = lex.expect(TokenType.KW_LET)
    id = lex.expect(TokenType.IDENT)
    if lex.next_is(TokenType.ASSIGN):
        _ = lex.expect(TokenType.ASSIGN)
        exp = parse_expr(lex, 1)
        _ = lex.expect(TokenType.SEMI)
        return NDeclare(id, exp)
    elif lex.next_is(TokenType.SEMI):
        _ = lex.expect(TokenType.SEMI)
        return NDeclare(id, NTerm(0))
    error(f"{lex.peek().loc}: ERROR: Expected {tok_to_str[TokenType.ASSIGN]} or {tok_to_str[TokenType.SEMI]} but found {tok_to_str[lex.peek().type]}")

def parse_assign(lex: Lexer) -> NAssign:
    vid = lex.expect(TokenType.IDENT)
    _ = lex.expect(TokenType.ASSIGN)
    exp = parse_expr(lex, 1)
    _ = lex.expect(TokenType.SEMI)
    return NAssign(vid, exp)

def parse_read(lex: Lexer) -> NRead:
    _ = lex.expect(TokenType.KW_READ)
    id = lex.expect(TokenType.IDENT)
    _ = lex.expect(TokenType.SEMI)
    return NRead(id)

def parse_print(lex: Lexer) -> NPrint:
    _ = lex.expect(TokenType.KW_PRINT)
    exp = parse_expr(lex, 1)
    _ = lex.expect(TokenType.SEMI)
    return NPrint(exp)

def parse_ifelse(lex: Lexer) -> NIfElse:
    _ = lex.expect(TokenType.KW_IF)
    cond = parse_expr(lex, 1)
    then_sc = parse_scope(lex)
    if lex.next_is(TokenType.KW_ELSE):
        lex.expect(TokenType.KW_ELSE)
        else_sc = parse_scope(lex)
        return NIfElse(cond, then_sc, else_sc)
    return NIfElse(cond, then_sc, None)

def parse_while(lex: Lexer):
    _ = lex.expect(TokenType.KW_WHILE)
    cond = parse_expr(lex, 1)
    body = parse_scope(lex)
    return NWhile(cond, body)

def parse_store(lex: Lexer) -> Statement:
    lex.expect(TokenType.AND)
    addr = parse_term(lex)
    lex.expect(TokenType.ASSIGN)
    val = parse_expr(lex, 1)
    lex.expect(TokenType.SEMI)
    return NStore(addr, val)

def parse_statement(lex: Lexer) -> Statement:
    if lex.next_is(TokenType.KW_LET):
        return parse_declare(lex)
    elif lex.next_is(TokenType.IDENT):
        return parse_assign(lex)
    elif lex.next_is(TokenType.KW_PRINT):
        return parse_print(lex)
    elif lex.next_is(TokenType.KW_READ):
        return parse_read(lex)
    elif lex.next_is(TokenType.CURL_OP):
        return parse_scope(lex)
    elif lex.next_is(TokenType.KW_IF):
        return parse_ifelse(lex)
    elif lex.next_is(TokenType.KW_WHILE):
        return parse_while(lex)
    elif lex.next_is(TokenType.AND):
        return parse_store(lex)
    else:
        # TODO: rewitre
        error(f"{lex.peek().loc}: ERROR: Expected {tok_to_str[TokenType.KW_LET]} " +\
                                                   tok_to_str[TokenType.IDENT] + ", " +\
                                                   tok_to_str[TokenType.KW_PRINT] + ", "+\
                                                   tok_to_str[TokenType.KW_WHILE] + ", "+\
                                                   tok_to_str[TokenType.KW_READ] + " or " +\
                                                   tok_to_str[TokenType.CURL_OP] + f" but found {tok_to_str[lex.peek().type]}")

def parse_scope(lex: Lexer) -> NScope:
    lex.expect(TokenType.CURL_OP)
    stmts = []
    while not lex.next_is(TokenType.CURL_CL):
        stmts.append(parse_statement(lex))
    lex.expect(TokenType.CURL_CL)
    return NScope(stmts)

def parse_prog(lex: Lexer) -> NProg:
    stmts = []
    while not lex.next_is(TokenType.EOF):
        stmts.append(parse_statement(lex))
    return NProg(stmts)