from definitions import *

head = 0
sp = 0
bfvars = {}
bf_code = ""

# TODO: make comments and formating optional

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
    return f" t{res} "

def store(addr: int):
    global sp
    res = f"{to(addr)}[-]{to(sp-1)}[-{to(addr)}+{to(sp-1)}]"
    sp -= 1
    return f"store({addr}): {res}\n"

def top(addr: int):
    global sp
    res = f"{to(addr)}[-{to(sp)}+{to(sp+1)}+{to(addr)}]{to(sp+1)}[-{to(addr)}+{to(sp+1)}]"
    sp += 1
    return f"top({addr}): {res}\n"

def pushint(n: int):
    global sp
    res = to(sp) + '[-]' + '+'*n
    sp += 1
    return f"pushint({n}): {res}\n"

#def addto(src, dst):
#    return f"{to(src)}[-{to(dst)}+{to(src)}]"

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
    else:
        error("Unreacheable")

def gen_binop(op: BinOpKind):
    global head
    res = ""
    # a b ^
    match op:
        case BinOpKind.ADD:
            res = f"add: {to(sp-1)}[-<+>]\n"
        case BinOpKind.SUB:
            res = f"sub: {to(sp-1)}[-<->]\n"
        case BinOpKind.MULT:
            res = f"mult: {to(sp-2)}>>[-]>[-]<<<[->>+<<]>[->[-<<+>>>+<]>[-<+>]<<]<\n"
        case BinOpKind.DIV:
            raise NotImplementedError()
    return res
        

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
    return res

def gen_read(node: NPrint):
    global sp
    assert isinstance(node, NRead)
    id = node.id
    if not(id.val in bfvars.keys()):
        error(f"{id.loc}: ERROR: Variable `{id.val}` not declared.")
    res = to(sp)+','
    sp += 1 
    res += store(bfvars[id.val])
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
    else:
        raise AssertionError("Unreacheable statement")

def gen_prog(node: NProg):
    assert isinstance(node, NProg)
    return "".join(gen_statement(s) for s in node.stmts)