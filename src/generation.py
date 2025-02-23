from definitions import *
#_A_A0...N

MAX_NESTING = 100
head = hp = sp = 0
sp = hp+1
bfvars = {}
bfmacros = {}
nesting = 0
# TODO: make comments and formating optional

cmp = "[-]>[-]<<<[->>+>+<<<]>>>[-<<<+>>>][-]>[-]<<<[->>+>+<<<]>>>[-<<<+>>>][-]<<[>[>+<[-]]<[-]]>>[-<<+>>]<<[<<->->>[-]>[-]<<<<[->>>+>+<<<<]>>>>[-<<<<+>>>>][-]>[-]<<<<[->>>+>+<<<<]>>>>[-<<<<+>>>>][-]<<[>[>+<[-]]<[-]]>>[-<<+>>]<<<[-]>[-<+>]<]"
 

def define_macro(macro: NMacroDef):
    if macro.name.val in bfmacros.keys():
        error(f"{macro.name.loc}: ERROR: Redefinition of macro `{macro.name.val}`")
    bfmacros.update({macro.name.val: macro}) # TODO: i don't like that name still stores as token
    
def to(addr):
    global head, sp
    steps = addr-head
    head = addr
    res = ''
    if steps < 0:
        steps *= -1
        res = '<'*steps
    else:
        res = '>'*steps
    return res

def store(addr: int):
    global sp
    res = f"{to(addr)}[-]{to(sp-1)}[-{to(addr)}+{to(sp-1)}]\n"
    sp -= 1
    return res

def top(addr: int):
    global sp
    res = f"{to(sp)}[-]>[-]<{to(addr)}[-{to(sp)}+{to(sp+1)}+{to(addr)}]{to(sp+1)}[-{to(addr)}+{to(sp+1)}]\n"
    sp += 1
    return res

def pushint(n: int):
    global sp
    res = to(sp) + '[-]' + '+'*n
    sp += 1
    return res+'\n'

#def addto(src, dst):
#    return f"{to(src)}[-{to(dst)}+{to(src)}]"

def gen_load(node: NLoad):
    assert isinstance(node, NLoad)
    global sp, hp, head
    p = sp
    res = gen_expr(node.addr)
    res += f"{to(p)}>[-]>[-]<<" # zero 2 cells after p, the head at p
    res += f"[-{to(p+1)}+{to(hp-2)}+{to(p)}]" # copy p to p+1 and hp-2 (first counter cell in heap), the head at p
    res += to(hp-2)
    res += "[[-<<+>>]+<<-]+" # while counter > 0 move it one cell left, set curent pos to 1, decrement
    res += ">[" # while cell with addres `counter` > 0
    res += "-<<<+>>"
    res += "[->>]" # follow tail of ones, after this the head at hp
    head = hp
    res += to(p)+'+'+to(p+1) # inc p, the head at p+1
    res += f"[-{to(p+2)}+{to(hp-2)}+{to(p+1)}]"  # copy p+1 to p+2 and hp-2 (first counter cell in heap), the head at p+1
    res += f"{to(p+2)}[-<+>]" # move p+2 to p+1, the head at p+2
    res += to(hp-2)
    res += "[[-<<+>>]+<<-]+" # while counter > 0 move it one cell left, set curent pos to 1, decrement
    res += ">]<<<[->>>+<<<]>>>" # the head at cell with addres `counter`
    res += "<[->>]" # follow tail of ones, after this the head at hp
    head = hp
    return res

def gen_not(node: NNot):
    assert isinstance(node, NNot)
    global sp
    res = ''
    addr = sp
    res += to(sp)
    res += "[-]+"
    sp += 1
    res += gen_term(node.expr)
    res += to(addr)
    res += ">[<[-]>[-]]<"
    sp = addr + 1
    return res

def get_nesting(name: str) -> int:
    global nesting, bfvars
    for n in range(nesting, -1, -1):
        if '.'*n+name in bfvars.keys():
            return n
    return -1

def gen_term_from_tok(tok: Token):
    global bfvars
    assert isinstance(tok, Token)
    match tok.type:
        case TokenType.INTLIT:
            return pushint(int(tok.val))
        case TokenType.CHAR:
            return pushint(ord(tok.val))
        case TokenType.IDENT:
            name = tok.val
            nest = get_nesting(name)
            if nest < 0:
                error(f"{tok.loc}: ERROR: Variable `{tok.val}` not declared.")
            return top(bfvars['.'*nest+name])
        case _:
            assert False, "Unreachable"

def gen_term(node: NTerm):
    global nesting
    assert isinstance(node, NTerm)
    val = node.val
    if isinstance(val, Token):
        return gen_term_from_tok(val)
    elif isinstance(val, NLoad): #TODO: deprecate
        return gen_load(val)
    elif isinstance(val, NNot):
        return gen_not(val)
    elif isinstance(val, NMacroUse):
        if not(val.name.val in bfmacros.keys()):
            error(f"{val.name.loc}: ERROR: Macro `{val.name.val}` not declared.")
        if not bfmacros[val.name.val].is_func:
            error(f"{val.name.loc}: ERROR: Macro `{val.name.val}` does not return any value, but used in expression.")
        return gen_macro(val)
    else:
        assert False, f"Unreacheable {val.__class__}"

def gen_binop(op: BinOpKind):
    global head
    res = ""
    # a b ^
    match op:
        case BinOpKind.ADD:
            res = f"{to(sp-1)}[-<+>]"
        case BinOpKind.SUB:
            res = f"{to(sp-1)}[-<->]"
        case BinOpKind.MULT:
            res = f"{to(sp-2)}>>[-]>[-]<<<[->>+<<]>[->[-<<+>>>+<]>[-<+>]<<]<"
        case BinOpKind.DIV:
            raise NotImplementedError()
        case BinOpKind.AND:
            res = f"{to(sp)}[-]<<[>[>+<[-]]<[-]]>>[-<<+>>]"
        case BinOpKind.OR:
            res = f"{to(sp)}[-]<<[>>+<<[-]]>[>+<[-]]>[<<+>>[-]]"
        case BinOpKind.EQ:
            res = f"{to(sp-2)}[->-<]+>[<[-]>[-]]<"
        case BinOpKind.NEQ:
            res = f"{to(sp-2)}[->-<]>[<+>[-]]<"
        case BinOpKind.LESS:
            res = to(sp) + cmp + '<<[-]>[<+>[-]]>'
        case BinOpKind.LESSEQ:
            res = to(sp) + cmp + '<[-]<[->+<]+>[<[-]>[-]]>'
        case BinOpKind.GREATER:
            res = to(sp) + cmp + '<[-]<[->+<]>[<+>[-]]>'
        case BinOpKind.GREATEREQ:
            res = to(sp) + cmp + '<<[-]+>[<[-]>[-]]>'
        case _:
            raise AssertionError("Unreacheable")
    return res+'\n'
        

def gen_bin_expr(node: NBinExpr):
    global sp
    assert isinstance(node, NBinExpr)
    res = \
    gen_expr(node.lhs) +\
    gen_expr(node.rhs) +\
    gen_binop(node.op)
    sp -= 1
    return res

def gen_expr(node: Expr):
    if isinstance(node, NTerm):
        return gen_term(node)
    elif isinstance(node, NBinExpr):
        return gen_bin_expr(node)
    else:
        raise TypeError(node.__class__)

def gen_declare(node: NDeclare):
    global bfvars, sp, nesting
    assert isinstance(node, NDeclare)
    id, exp = node.id, node.val

    if '.'*nesting+id.val in bfvars.keys():
        error(f"{id.loc}: ERROR: Variable `{id.val}` already declared.")

    if get_nesting(id.val) >= 0: print(f"{id.loc}: WARNING: Variable shadowing. Variable `{id.val}` declared in an outer scope.")
    addr = sp
    bfvars.update({'.'*nesting+id.val: addr})
    
    sp += 1
    gened_expr: str
    if exp == None:
        gened_expr = pushint(0)
    else:
        gened_expr = gen_expr(exp)
    return gened_expr + store(addr)

def gen_assign(node: NAssign):
    assert isinstance(node, NAssign)
    id = node.id

    nest = get_nesting(id.val)
    if nest < 0:
        error(f"{id.loc}: ERROR: Variable `{id.val}` not declared.")
    name = '.'*nest+id.val
    return gen_expr(node.val) + store(bfvars[name])

def gen_print(node: NPrint):
    global sp
    assert isinstance(node, NPrint)
    res = gen_expr(node.expr)+to(sp-1)+"."
    sp -= 1
    return res+'\n'

def gen_read(node: NPrint):
    global sp
    assert isinstance(node, NRead)
    id = node.id
    nest = get_nesting(id.val)
    if nest < 0:
        error(f"{id.loc}: ERROR: Variable `{id.val}` not declared.")
    name = '.'*nest+id.val
    res = to(sp)+','
    sp += 1 
    res += store(bfvars[name])
    return res+'\n'

def gen_scope(node: NScope):
    assert isinstance(node, NScope)
    global sp, bfvars, nesting
    res = ''
    vars_c = len(bfvars)
    sp_ = sp

    nesting += 1
    res += '\n'.join(map(gen_statement, node.stmts))
    nesting -= 1

    for _ in range(len(bfvars)-vars_c):
        bfvars.popitem()
    sp = sp_
    return res

def gen_ifelse(node: NIfElse): #TODO rewite normal way!!!
    assert isinstance(node, NIfElse)
    res = ''
    global sp
    res += gen_expr(node.cond)
    cond = sp-1
    flag = sp
    sp += 1
    if node.elze != None: res += f"{to(flag)}[-]+\n"
    res += f"{to(cond)}[{gen_scope(node.then)}\n"
    if node.elze != None: res += f"{to(flag)}[-]\n"
    res += f"{to(cond)}[-]]\n"
    if node.elze != None:
        res += f"{to(flag)}[{gen_scope(node.elze)}{to(flag)}[-]]\n"
    sp -= 2
    return res

def gen_while(node: NWhile):
    assert isinstance(node, NWhile)
    global sp
    cond_addr = sp
    res = gen_expr(node.cond)
    res += f"{to(cond_addr)}[\n{gen_scope(node.body)}\n{gen_expr(node.cond)}{store(cond_addr)}{to(cond_addr)}]"
    sp -= 1
    return res

def gen_store(node):
    assert isinstance(node, NStore)
    global sp, hp, head
    res = ""
    addr = sp
    res += gen_expr(node.addr)
    val = sp
    res += gen_expr(node.val)
    res += f"{to(addr)}>>[-]<<[-{to(hp-2)}+{to(addr+2)}+{to(addr)}]"
    res += f">>[-<<+>>]<<"
    res += to(hp-2)
    res += "[[-<<+>>]+<<-]+" # while counter > 0 move it one cell left, set curent pos to 1, decrement
    res += ">[-]<"
    res += "[->>]"
    head = hp
    res += to(val)
    res += "[-" #while value is not zero
    res += f"{to(addr)}[-{to(hp-2)}+{to(addr+2)}+{to(addr)}]"
    res += f">>[-<<+>>]<<"
    res += to(hp-2)
    res += "[[-<<+>>]+<<-]+" # while counter > 0 move it one cell left, set curent pos to 1, decrement
    res += ">+<"
    res += "[->>]"
    head = hp
    res += to(val)
    res += "]"
    sp -= 2
    return res


def gen_macro(node):
    global nesting, sp, bfvars
    assert isinstance(node, NMacroUse)
    if nesting > MAX_NESTING:
        error(f"{node.name.loc}: ERROR: Maximum nesting level exeeded while generating `{node.name.val}` macro. Macros don't support recursion!")
    if not(node.name.val in bfmacros.keys()):
        error(f"{node.name.loc}: ERROR: Macro `{node.name.val}` not declared.")

    macro: NMacroDef = bfmacros[node.name.val]

    if len(macro.args) != len(node.args):
        error(f"{node.name.loc}: ERROR: Macro `{macro.name.val}` takes {len(macro.args)} arguments but got {len(node.args)}.")

    res = ''
    argc = len(macro.args)
    _sp = sp
    nesting += 1
    if macro.is_func:
        addr = sp
        res += pushint(0)
        bfvars.update({'.'*(nesting)+"Result": addr})
        
    for i in range(argc):
        addr = sp
        res += gen_expr(node.args[i])
        bfvars.update({'.'*(nesting)+macro.args[i].val: addr})
        
    nesting -= 1
    res += gen_scope(macro.body)
    for _ in range(argc):
        bfvars.popitem()

    sp = _sp
    if macro.is_func:
        bfvars.popitem()
        sp += 1
    return res

def gen_str(node: NStr):
    assert isinstance(node, NStr)
    global sp
    res = to(sp) + '[-]'
    val = 0
    for c in node.string:
        diff = ord(c) - val
        if diff >= 0:
            res += '+'*diff + '.'
        else:
            res += '-'*(-1*diff) + '.'
        val = ord(c)
    return res

def gen_statement(node: Statement):
    if isinstance(node, NDeclare):
        return gen_declare(node)
    elif isinstance(node, NAssign):
        return gen_assign(node)
    elif isinstance(node, NPrint):
        return gen_print(node)
    elif isinstance(node, NRead):
        return gen_read(node)
    elif isinstance(node, NScope):
        return gen_scope(node)
    elif isinstance(node, NIfElse):
        return gen_ifelse(node)
    elif isinstance(node, NWhile):
        return gen_while(node)
    elif isinstance(node, NStore):
        return gen_store(node)
    elif isinstance(node, NMacroDef):
        define_macro(node)
        return ''
    elif isinstance(node, NMacroUse):
        if not(node.name.val in bfmacros): error(f"{node.name.loc}: ERROR: Macro `{node.name.val}` not declared.")
        if bfmacros[node.name.val].is_func: print(f"{node.name.loc}: WARNING: Memory leak: Macro `{node.name.val}` returns value that not used.")
        return gen_macro(node)
    elif isinstance(node, NStr):
        return gen_str(node)
    else:
        assert False, "Unreacheable statement"

def gen_prog(node: NProg, heap: int, formatting=False):
    assert isinstance(node, NProg)
    global head, hp, sp, bfvars #TODO: I dont like it at all
    head = 0
    hp = heap*2+1
    sp = hp+1
    bfvars = {}
    code = "\n".join(gen_statement(s) for s in node.stmts)
    if formatting:
        return code
    
    return ''.join(filter(lambda x: x in '+-<>[],.', code))