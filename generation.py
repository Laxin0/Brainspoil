from definitions import *

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
    res = ""
    # a b ^
    match op:
        case BinOpKind.ADD:
            res = f"{to(sp-1)}[-<+>]"
        case BinOpKind.SUB:
            res = f"{to(sp-1)}[-<->]"
        case BinOpKind.MULT:
            res = f"{to(sp+1)}[-]<[-]<[-<[->>+<<]>>[>+<<<+>>]>[-<+>]<<]"
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

def gen_statement(node: Statement):
    if isinstance(node, NDeclare):
        return gen_declare(node)
    else:
        error("Unreacheable")

def gen_prog(node: NProg):
    assert isinstance(node, NProg)
    return "".join(gen_statement(s) for s in node.stmts)