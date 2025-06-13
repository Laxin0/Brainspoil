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
                while c.isalnum() or c == '_':
                    buff += c
                    self.index += 1
                    self.col += 1
                    if self.index >= len(self.src): break
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
                    if self.index >= len(self.src): break
                    c = self.src[self.index]
                return Token(TokenType.INTLIT, buff, loc)
            
            elif (self.index + 1) < len(self.src) and ((c + self.src[self.index+1]) in puncts.keys()): #TODO: make better (it's fucking disgusting)
                loc = self.loc()
                punc = c + self.src[self.index+1]
                self.index += 2
                self.col += 2
                return Token(puncts[punc], None, loc)
            elif c in puncts.keys():
                loc = self.loc()
                self.index += 1
                self.col += 1
                return Token(puncts[c], None, loc)
            elif c == '#': #TODO: make better
                while c != '\n':
                    self.index += 1
                    if self.index >= len(self.src):
                        return Token(TokenType.EOF, None, self.loc())
                    c = self.src[self.index]
                self.col = 1
                self.index += 1
                self.line += 1
            elif c == '\'': #TODO: make better. It's so bad omg. 
                loc = self.loc()
                self.index += 1; self.col += 1
                if self.index >= len(self.src): error(f"{self.loc()}: ERROR: Unexpected end of file.")
                char = ''
                current = self.src[self.index]
                if current == '\\':
                    self.index += 1; self.col += 1
                    if self.index >= len(self.src): error(f"{self.loc()}: ERROR: Unexpected end of file.")
                    if self.src[self.index] == '\n': error(f"{self.loc()}: ERROR: Character constant must be on one line.")
                    if not(self.src[self.index] in esc_chars.keys()): error(f"{self.loc()}: ERROR: Unknown escape character `{self.src[self.index]}`")
                    char = esc_chars[self.src[self.index]]
                elif current == '\n': error(f"{self.loc()}: ERROR: Character constant must be in the one line.")
                else:
                    char = current
                self.index += 1; self.col += 1
                if self.index >= len(self.src): error(f"{self.loc()}: ERROR: Unexpected end of file.")
                if self.src[self.index] != '\'': error(f"{self.loc()}: ERROR: Expected closing `'` in character constant, but found `{self.src[self.index]}`")
                self.index += 1; self.col += 1
                return Token(TokenType.CHAR, char, loc)
            elif c == '"':
                loc = self.loc()
                self.index += 1; self.col += 1
                if self.index >= len(self.src): error(f"{self.loc()}: ERROR: Unexpected end of file.")
                buff = ""
                while self.src[self.index] != '"':
                    if self.src[self.index] == '\n': error(f"{self.loc}: ERROR: String literal must be on one line.")
                    if self.src[self.index] == '\\':
                        self.index += 1; self.col += 1
                        if self.index >= len(self.src): error(f"{self.loc()}: ERROR: Unexpected end of file.")
                        if not(self.src[self.index] in esc_chars.keys()): error(f"{self.loc()}: ERROR: Unknown escape character `{self.src[self.index]}`")
                        buff += esc_chars[self.src[self.index]]
                    else:
                        buff += self.src[self.index]
                    self.index += 1; self.col += 1
                    if self.index >= len(self.src): error(f"{self.loc()}: ERROR: Unexpected end of file.")
                self.index += 1; self.col += 1
                return Token(TokenType.STRLIT, buff, loc)

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

    def get_next(self):
        cur = self.buffer
        self.buffer = self.next()
        return cur

macros = []

def parse_string(lex: Lexer) -> NStr:
    string = lex.expect(TokenType.STRLIT).val
    lex.expect(TokenType.SEMI)
    return NStr(string)

def parse_rvalue_from_id(lex: Lexer) -> Token|NMacroUse|NIndex:
    assert lex.peek().type == TokenType.IDENT
    if lex.peek().val in macros:
        return parse_macro_use(lex)
    
    ident = lex.expect(TokenType.IDENT)
    if lex.next_is(TokenType.SQR_OP):
        lex.expect(TokenType.SQR_OP)
        expr = parse_expr(lex, 1)
        lex.expect(TokenType.SQR_CL)
        return NIndex(ident, expr)
    return ident

def parse_term(lex: Lexer) -> Expr:
    if lex.next_is(TokenType.INTLIT):
        tok = lex.expect(TokenType.INTLIT)
        return NTerm(tok)
    elif lex.next_is(TokenType.IDENT): #TODO: think
        return NTerm(parse_rvalue_from_id(lex))
    elif lex.next_is(TokenType.PAREN_OP):
        tok = lex.expect(TokenType.PAREN_OP)
        exp = parse_expr(lex, 1)
        lex.expect(TokenType.PAREN_CL)
        return exp #TODO: wrap in NTerm
    elif lex.next_is(TokenType.CHAR):
        tok = lex.expect(TokenType.CHAR)
        return NTerm(tok)
    elif lex.next_is(TokenType.NOT):
        tok = lex.expect(TokenType.NOT)
        t = parse_term(lex)
        return NTerm(NNot(t))
    else:
        error(f"{lex.peek().loc}: ERROR: Expected {tok_to_str[TokenType.INTLIT]}, {tok_to_str[TokenType.IDENT]} or {tok_to_str[TokenType.PAREN_OP]} " +\
              f" but found {tok_to_str[lex.peek().type]}")


def parse_expr(lex: Lexer, min_prec) -> Expr:
    lhs = parse_term(lex)
    
    while True: 
        if (not lex.peek().type in ttype_to_binop.keys()) or binop_prec[ttype_to_binop[lex.peek().type]] < min_prec:
            break
        op = ttype_to_binop[lex.get_next().type]
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
        return NDeclare(id, None)
    error(f"{lex.peek().loc}: ERROR: Expected {tok_to_str[TokenType.ASSIGN]} or {tok_to_str[TokenType.SEMI]} but found {tok_to_str[lex.peek().type]}")

def parse_lvalue(lex: Lexer) -> Token|NIndex:
    ident = lex.expect(TokenType.IDENT)
    if lex.next_is(TokenType.SQR_OP):
        lex.expect(TokenType.SQR_OP)
        expr = parse_expr(lex, 1)
        lex.expect(TokenType.SQR_CL)
        return NIndex(ident, expr)
    return ident

def parse_assign(lex: Lexer) -> NAssign:
    lhs = parse_lvalue(lex)
    _ = lex.expect(TokenType.ASSIGN)
    exp = parse_expr(lex, 1)
    _ = lex.expect(TokenType.SEMI)
    return NAssign(lhs, exp)


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

def parse_macro_def(lex: Lexer) -> NMacroDef:
    lex.expect(TokenType.KW_MACRO)
    is_func = False
    if lex.next_is(TokenType.TIMES):
        lex.expect(TokenType.TIMES)
        is_func = True

    macro_name = lex.expect(TokenType.IDENT)
    macros.append(macro_name.val)
    lex.expect(TokenType.PAREN_OP)
    args = []
    if lex.next_is(TokenType.IDENT):
        name = lex.expect(TokenType.IDENT)
        args.append(Arg(name, False))
    elif lex.next_is(TokenType.REF):
        lex.expect(TokenType.REF)
        name = lex.expect(TokenType.IDENT)
        args.append(Arg(name, True))
    while lex.next_is(TokenType.COMMA):
        lex.expect(TokenType.COMMA)
        is_ref = False
        if lex.next_is(TokenType.REF):
            lex.expect(TokenType.REF)
            is_ref = True
        name = lex.expect(TokenType.IDENT)
        args.append(Arg(name, is_ref))

    lex.expect(TokenType.PAREN_CL)
    body = parse_scope(lex)

    return NMacroDef(is_func, macro_name, args, body)

def parse_macro_use(lex: Lexer) -> NMacroUse: # just allocate arguments on the stack like variables with name 'macro.arg'
    name = lex.expect(TokenType.IDENT)
    lex.expect(TokenType.PAREN_OP)
    args = []
    if lex.peek().type in [TokenType.INTLIT, TokenType.IDENT, TokenType.PAREN_OP,
                           TokenType.CHAR, TokenType.NOT, TokenType.REF]: #TODO: fuck, i dont know.... I just want shit to be done
        if lex.next_is(TokenType.REF):
            lex.expect(TokenType.REF)
            ident = lex.expect(TokenType.IDENT)
            args.append(Arg(ident, True))
        else:
            args.append(Arg(parse_expr(lex, 0), False))

    while lex.next_is(TokenType.COMMA):
        lex.expect(TokenType.COMMA)
        if lex.next_is(TokenType.REF):
            lex.expect(TokenType.REF)
            ident = lex.expect(TokenType.IDENT)
            args.append(Arg(ident, True))
        else:
            args.append(Arg(parse_expr(lex, 0), False))
    lex.expect(TokenType.PAREN_CL)
    return NMacroUse(name, args)

def parse_const_decl(lex: Lexer) -> NConstDecl:
    lex.expect(TokenType.KW_CONST)
    ident = lex.expect(TokenType.IDENT)
    lex.expect(TokenType.ASSIGN)
    value: int
    if lex.next_is(TokenType.INTLIT):
        value = int(lex.expect(TokenType.INTLIT).val)
    elif lex.next_is(TokenType.CHAR):
        value = ord(lex.expect(TokenType.CHAR).val)
    else:
        error(f"{lex.peek().loc}: ERROR: Expected {tok_to_str[TokenType.INTLIT]} or {tok_to_str[TokenType.CHAR]} but found {tok_to_str[lex.peek().type]}")
    lex.expect(TokenType.SEMI)
    return NConstDecl(ident, value)

def parse_arr_decl(lex: Lexer):
    lex.expect(TokenType.KW_ARR)
    ident = lex.expect(TokenType.IDENT)
    lex.expect(TokenType.SQR_OP)

    size_param = lex.get_next()
    if size_param.type not in [TokenType.INTLIT, TokenType.IDENT]:
        error(f"{size_param.loc}: ERROR: Expected {tok_to_str[TokenType.INTLIT]} or {tok_to_str[TokenType.IDENT]} but found {tok_to_str[size_param.type]}.")
    lex.expect(TokenType.SQR_CL)
    lex.expect(TokenType.SEMI)
    return NArrDecl(ident, size_param)

def parse_statement(lex: Lexer) -> Statement:
    if lex.next_is(TokenType.KW_LET):
        return parse_declare(lex)
    elif lex.next_is(TokenType.KW_ARR):
        return parse_arr_decl(lex)
    elif lex.next_is(TokenType.KW_CONST):
        return parse_const_decl(lex)
    elif lex.next_is(TokenType.IDENT): # TODO: i don't like it
        name = lex.peek().val
        if name in macros:
            macro_use = parse_macro_use(lex)
            lex.expect(TokenType.SEMI)
            return macro_use
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
    elif lex.next_is(TokenType.KW_MACRO):
        return parse_macro_def(lex)
    elif lex.next_is(TokenType.STRLIT):
        return parse_string(lex)
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