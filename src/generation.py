from definitions import *
#_A_A0...N

HEAP_CAP = 32
head = 0
hp = HEAP_CAP*2+1
sp = hp+1
bfvars = {}
bfmacros = {}
local_name = ''
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

def gen_term(node: NTerm):
    assert isinstance(node, NTerm)
    val = node.val
    if isinstance(val, Token):
        assert val.type == TokenType.IDENT
        if not (val.val in bfvars.keys()):
            error(f"{val.loc}: ERROR: Vriable `{val.val}` not declared.")
        return top(bfvars[val.val])
    elif isinstance(val, int):
        return pushint(val)
    elif isinstance(val, NLoad):
        return gen_load(val)
    elif isinstance(val, NNot):
        return gen_not(val)
    else:
        assert False, "Unreacheable"

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
    global bfvars, sp
    assert isinstance(node, NDeclare)
    id, exp = node.id, node.val
    if id.val in bfvars.keys():
        error(f"{id.loc}: ERROR: Variable `{id.val}` already declared.")
    addr = sp
    bfvars.update({id.val: addr})
    sp += 1
    return gen_expr(exp) + store(addr)

def gen_assign(node: NAssign):
    assert isinstance(node, NAssign)
    id = node.id
    if not(id.val in bfvars.keys()):
        error(f"{id.loc}: ERROR: Variable `{id.val}` not declared.")
    
    return gen_expr(node.val) + store(bfvars[id.val])

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
    if not(id.val in bfvars.keys()):
        error(f"{id.loc}: ERROR: Variable `{id.val}` not declared.")
    res = to(sp)+','
    sp += 1 
    res += store(bfvars[id.val])
    return res+'\n'

def gen_scope(node: NScope):
    assert isinstance(node, NScope)
    global sp, bfvars
    res = ''
    vars_c = len(bfvars)
    sp_ = sp

    res += '\n'.join(map(gen_statement, node.stmts))
    
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
    else:
        assert False, "Unreacheable statement"

def gen_prog(node: NProg, heap: int, formatting=False):
    assert isinstance(node, NProg)
    global HEAP_CAP, head, hp, sp, bfvars #TODO: I dont like it at all
    HEAP_CAP = 32
    head = 0
    hp = HEAP_CAP*2+1
    sp = hp+1
    bfvars = {}
    code = "\n".join(gen_statement(s) for s in node.stmts)
    if formatting:
        return code
    
    return ''.join(filter(lambda x: x in '+-<>[],.', code))