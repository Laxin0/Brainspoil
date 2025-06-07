from definitions import *
#_A_A0...N

MAX_NESTING = 100
head = hp = sp = 0
sp = hp+1

bfnames = {}

#bfvars = {}
#bfconsts = {}
#bfmacros = {}
nesting = 0
# TODO: make comments and formating optional

cmp = "[-]>[-]<<<[->>+>+<<<]>>>[-<<<+>>>][-]>[-]<<<[->>+>+<<<]>>>[-<<<+>>>][-]<<[>[>+<[-]]<[-]]>>[-<<+>>]<<[<<->->>[-]>[-]<<<<[->>>+>+<<<<]>>>>[-<<<<+>>>>][-]>[-]<<<<[->>>+>+<<<<]>>>>[-<<<<+>>>>][-]<<[>[>+<[-]]<[-]]>>[-<<+>>]<<<[-]>[-<+>]<]"

# def get_arr(id: Token):
#     assert isinstance(id, Token)
#     if not id.val in bfnames.keys() and isinstance():
#         error(f"{id.loc}: ERROR: Array `{id.val}` not declared.")
#     return bfarrs[id.loc]

def get_macro(node: NMacroUse) -> NMacroDef:
    assert isinstance(node, NMacroUse)
    if node.name.val in bfnames.keys() and isinstance(bfnames[node.name.val], NMacroDef):
        return bfnames[node.name.val]
    error(f"{node.name.loc}: ERROR: Macro `{node.name.val}` not defined.")

def get_var(id: Token) -> int:
    assert isinstance(id, Token) and id.type == TokenType.IDENT, f"got: {id}"
    nest = get_nesting(id.val)
    if nest < 0:
        error(f"{id.loc}: ERROR: Variable `{id.val}` not declared.")
    return bfnames[("."*nest)+id.val].addr

def define_macro(macro: NMacroDef):
    if macro.name.val in bfnames.keys() and isinstance(bfnames[macro.name.val], NMacroDef):
        error(f"{macro.name.loc}: ERROR: Redefinition of macro `{macro.name.val}`")
    if macro.name.val in bfnames.keys():
        error(f"{macro.name.loc}: ERROR: Name `{macro.name.val}` already used.")
    if nesting > 0:
        error(f"{macro.name.loc}: ERROR: Macro can't be defined inside any scope.")
    bfnames.update({macro.name.val: macro}) # TODO: i don't like that name still stores as token
    
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

def store(addr: int, size: int):
    global sp
    res = ''
    for n in range(size):
        res += to(addr+n) + "[-]"
    for n in range(size):
        res += to(sp-size+n) + "[-" + to(addr+n) + "+" + to(sp-size+n) + "]"
    sp -= size
    return res

def top(addr: int, size: int):
    global sp
    res = ''
    for n in range(size):
        res += to(sp+n) + "[-]" + to(sp+n+size) + "[-]"
    for n in range(size):
        res += to(addr+n) + "[-" + to(sp+n) + "+" + to(sp+n+size) + "+" + to(addr+n) + "]" + to(sp+n+size) + "[-" + to(addr+n) + "+" + to(sp+n+size) + "]"
    sp += size
    return res

def pushint(n: int):
    global sp
    res = to(sp) + '[-]' + '+'*n
    sp += 1
    return res+'\n'

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
    global nesting, bfnames
    for n in range(nesting, -1, -1):
        nname = '.'*n+name
        if nname in bfnames.keys():
            return n
    return -1

def gen_term_from_tok(tok: Token):
    global bfnames
    assert isinstance(tok, Token)
    match tok.type:
        case TokenType.INTLIT:
            return pushint(int(tok.val))
        case TokenType.CHAR:
            return pushint(ord(tok.val))
        case TokenType.IDENT:
            if tok.val in bfnames.keys() and isinstance(bfnames[tok.val], ConstData):
                return pushint(bfnames[tok.val].val)
            addr = get_var(tok)
            return top(addr, 1)
        case _:
            assert False, "Unreachable"

def gen_term(node: NTerm):
    global nesting
    assert isinstance(node, NTerm)
    val = node.val
    if isinstance(val, Token):
        return gen_term_from_tok(val)
    elif isinstance(val, NNot):
        return gen_not(val)
    elif isinstance(val, NMacroUse):
        macro = get_macro(val)
        if not macro.is_func: #TODO: This code may be dead
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
    global bfnames, sp, nesting
    assert isinstance(node, NDeclare)
    id, exp = node.id, node.val

    name = '.'*nesting+id.val
    if name in bfnames.keys() and isinstance(bfnames[name], VarData):
        error(f"{id.loc}: ERROR: Variable `{id.val}` already declared.")
    if name in bfnames.keys():
         error(f"{id.loc}: ERROR: Name `{id.val}` already used.") #TODO: by who or at least what type

    if get_nesting(id.val) >= 0: print(f"{id.loc}: WARNING: Name shadowing. Name `{id.val}` used in an outer scope.")
    addr = sp
    bfnames.update({name: VarData(addr)})
    
    sp += 1
    gened_expr: str
    if exp == None:
        gened_expr = ''
    else:
        gened_expr = gen_expr(exp)
    return gened_expr + store(addr, 1)

def gen_load(node: NIndex):
    assert isinstance(node, NIndex)
    global sp, head
    arr_addr = get_arr(node.id)
    p = sp
    res =  gen_expr(node.index)
    res += f"{to(p)}>[-]>[-]<<" # zero 2 cells after p, the head at p
    res += f"[-{to(p+1)}+{to(arr_addr-2)}+{to(p)}]" # copy p to p+1 and arr_addr-2 (first counter cell in arr), the head at p
    res += to(arr_addr-2)
    res += "[[-<<+>>]+<<-]+" # while counter > 0 move it one cell left, set curent pos to 1, decrement
    res += ">[" # while cell with addres `counter` > 0
    res += "-<<<+>>"
    res += "[->>]" # follow tail of ones, after this the head at arr_addr
    head = arr_addr
    res += to(p)+'+'+to(p+1) # inc p, the head at p+1
    res += f"[-{to(p+2)}+{to(arr_addr-2)}+{to(p+1)}]"  # copy p+1 to p+2 and arr_addr-2 (first counter cell in arr), the head at p+1
    res += f"{to(p+2)}[-<+>]" # move p+2 to p+1, the head at p+2
    res += to(arr_addr-2)
    res += "[[-<<+>>]+<<-]+" # while counter > 0 move it one cell left, set curent pos to 1, decrement
    res += ">]<<<[->>>+<<<]>>>" # the head at cell with addres `counter`
    res += "<[->>]" # follow tail of ones, after this the head at arr_addr
    head = arr_addr
    return res

def gen_sp_to_arr(node: NIndex, val_expr: Expr):
    assert isinstance(node, NIndex)
    global sp, head
    res = ""
    arr_addr = get_arr(node.id)
    index_addr = sp
    res += gen_expr(node.index)
    val_addr = sp
    res += gen_expr(val_expr)
    res += f"{to(index_addr)}>>[-]<<[-{to(arr_addr-2)}+{to(index_addr+2)}+{to(index_addr)}]"
    res += f">>[-<<+>>]<<"
    res += to(arr_addr-2)
    res += "[[-<<+>>]+<<-]+" # while counter > 0 move it one cell left, set curent pos to 1, decrement
    res += ">[-]<"
    res += "[->>]"
    head = arr_addr
    res += to(val_addr)
    res += "[-" #while value is not zero
    res += f"{to(index_addr)}[-{to(arr_addr-2)}+{to(index_addr+2)}+{to(index_addr)}]"
    res += f">>[-<<+>>]<<"
    res += to(arr_addr-2)
    res += "[[-<<+>>]+<<-]+" # while counter > 0 move it one cell left, set curent pos to 1, decrement
    res += ">+<"
    res += "[->>]"
    head = arr_addr
    res += to(val_addr)
    res += "]"
    sp -= 2
    return res

def gen_assign(node: NAssign):
    assert isinstance(node, NAssign)

    #if isinstance(node.lhs, NIndex):
        

    id = node.lhs
    var = get_var(id)
    return gen_expr(node.rhs) + store(var, 1)

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
    var = get_var(id)
    res = to(sp)+','
    sp += 1 
    res += store(var, 1) #TODO: optimize
    return res+'\n'

def gen_scope(node: NScope):
    assert isinstance(node, NScope)
    global sp, bfnames, nesting
    res = ''
    vars_c = len(bfnames)
    sp_ = sp

    nesting += 1
    res += '\n'.join(map(gen_statement, node.stmts))
    nesting -= 1

    for _ in range(len(bfnames)-vars_c):
        bfnames.popitem()
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
    res += f"{to(cond_addr)}[\n{gen_scope(node.body)}\n{gen_expr(node.cond)}{store(cond_addr, 1)}{to(cond_addr)}]"
    sp -= 1
    return res

def gen_macro(node):
    global nesting, sp, bfnames
    assert isinstance(node, NMacroUse)
    if nesting > MAX_NESTING:
        error(f"{node.name.loc}: ERROR: Maximum nesting level exeeded while generating `{node.name.val}` macro. Macros don't support recursion!")

    macro = get_macro(node)
    if len(macro.args) != len(node.args):
        error(f"{node.name.loc}: ERROR: Macro `{macro.name.val}` takes {len(macro.args)} arguments but got {len(node.args)}.")

    res = ''
    argc = len(macro.args)
    _sp = sp
    nesting += 1
    if macro.is_func:
        addr = sp #TODO initialize or something else
        bfnames.update({'.'*(nesting)+"Result": VarData(addr)})
        
    for i in range(argc):
        if macro.args[i].is_ref:
            if not node.args[i].is_ref:
                error(f"{node.name.loc}: ERROR: {i+1}th arg must be passed by reference.")
            addr = get_var(node.args[i].val)
            bfnames.update({'.'*(nesting)+macro.args[i].val.val: VarData(addr)})
        else:
            if node.args[i].is_ref:
                error(f"{node.name.loc}: ERROR: {i+1}th arg must be passed by value.")
            addr = sp
            res += gen_expr(node.args[i].val)
            bfnames.update({'.'*(nesting)+macro.args[i].val.val: VarData(addr)})
        
    nesting -= 1
    res += gen_scope(macro.body)
    for _ in range(argc):
        bfnames.popitem()

    sp = _sp
    if macro.is_func:
        bfnames.popitem()
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

def gen_const_decl(node: NConstDecl):
    global nesting
    assert isinstance(node, NConstDecl)
    name = "."*nesting + node.id.val 
    if name in bfnames.keys() and isinstance(bfnames[node.id.val], ConstData):
        error(f"{node.id.loc}: ERROR: Constant `{node.id.val}` already declared.")
    if name in bfnames.keys() and not isinstance(bfnames[node.id.val], ConstData):
        error(f"{node.id.loc}: ERROR: Name `{node.id.val}` already used.") #TODO: by who?
    if get_nesting(node.id.val) >= 0: print(f"{node.id.loc}: WARNING: Name shadowing. Name `{node.id.val}` used in an outer scope.")

    bfnames.update({name: ConstData(node.val)})
    return ""


def gen_statement(node: Statement):
    if isinstance(node, NDeclare):
        return gen_declare(node)
    elif isinstance(node, NConstDecl):
        return gen_const_decl(node)
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
    elif isinstance(node, NMacroDef):
        define_macro(node)
        return ''
    elif isinstance(node, NMacroUse):
        macro = get_macro(node)
        if macro.is_func: print(f"{node.name.loc}: WARNING: Memory leak: Macro `{node.name.val}` returns value that not used.")
        return gen_macro(node)
    elif isinstance(node, NStr):
        return gen_str(node)
    else:
        assert False, "Unreacheable statement"

def gen_prog(node: NProg, heap: int, formatting=False):
    assert isinstance(node, NProg)
    global head, hp, sp #TODO: I dont like it at all
    head = 0
    hp = heap*2+1
    sp = hp+1
    bfnames = {}
    code = "\n".join(gen_statement(s) for s in node.stmts)
    if formatting:
        return code
    
    return ''.join(filter(lambda x: x in '+-<>[],.', code))
