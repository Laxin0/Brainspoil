# Gramar
NProg     ::= [Statement]
Statement ::= NDeclare
            | NAssign
            | NRead
            | NPrint
            | NScope
            | NIfElse
            | NWhile
            | NMacroDef
            | NmacroUse

NScope    ::= `{` [Statement] `}`

Expr      ::= NTerm 
            | NBinExpr

NTerm     ::= Token(int|char|str)
			| *NIndex*
            | `(` Expr `)`
            | NNot
            | NMacroUse
            

NBinExpr   ::= Expr BinOp Expr

NIfElse   ::= `if` Expr NScope {`else` NScope}

NWhile    ::= `while` Expr NScope  

NDeclare  ::= `let` Token(str) | *NIndex* {`=` Expr} `;`

NConstDecl ::= `const` Token(str) `=` Token(int|char) `;`

NAssign   ::= Token(str) | *NIndex* = Expr `;`
NPrint    ::= `print` Expr `;`
NRead     ::= `read` Token(str) | *NIndex* `;`
*NIndex   ::= Token(str) `[` Expr `]`*
NNot      ::= `!` Term

# My thoughts (Don't read)



if binop:
    error({at}: exp {}type but got Binexpr)

let a: Vec = (9 + 8);

assert_type(Term, exp_type):
    type = ...
    if type != exp: error("expected {exp_type} but got {type}")


BinExpr -> u8
Term -> Any

GenBinExpr: left.type == u8 and right.type == u8
         assert_type(lhs, u8)
        error(only u8 in bin expr)
         assert_type(rhs, u8)

GenDecl(a, Vec, binexpr):
    assert_type(binexpr, Vec)

!a

a and b => i if all 1. 0 if any 0

a b
^
>>[-]<<
[ at a
    > at b
    [
        >>+<<
        [-]
    ]
    <
    [-]
]
>>[-<<+>>]<<

a or b: 1 if any 1. 0 if all 0

a b
^

>>[-]++<<
[ at a
    >>-<<
    > at b
    [
        >>-<<
        [-]
    ]
    <
    [-]
]
>>[-<<+>>]<<


MULTIPLICATION = >>[-]>[-]<<<[->>+<<]>[->[-<<+>>>+<]>[-<+>]<<]<

>>>>>[-]<<<<<

a b c _ _ _ _
^

[->>>+>>+<<<<<]>>>>>[-<<<<<+>>>>>]<<<<<

a b c a`_ _ _
^

> [->>>+>+<<<<]>>>>[-<<<<+>>>>]<<<<<

a b c a`b`_ _
^
>>[-]<<[>[>+<[-]]<[-]]

0 0 & a`b`_ _
^

>>[

    
]

f"{to(cond_addr)}[\n{gen_scope(node.body)}\n{gen_expr(node.cond)}{store(cond_addr)}{to(cond_addr)}]"
>>>>>> skip heap
[-]++++++ push 6
<[-]>[-<+>] store
>[-]+++++push 5
<[-]>[-<+>] store
[-]<<[->>+>+<<<]>>>[-<<<+>>>] top a
[-]<<[->>+>+<<<]>>>[-<<<+>>>] top b

[-]<<[>[>+<[-]]<[-]]>>[-<<+>>] a && b
<<[ while
    >[-]<<<[->>>+>+<<<<]>>>>[-<<<<+>>>>] top a
    [-]+ push 1 
    [-<->] sub from a
    <<<<[-]>>>[-<<<+>>>] store a
    [-]<<[->>+>+<<<]>>>[-<<<+>>>] top b
    [-]+ push 1
    [-<->] sub from b
    <<<[-]>>[-<<+>>] store b
    [-]<<<[->>>+>+<<<<]>>>>[-<<<<+>>>>] top a
    [-]<<<[->>>+>+<<<<]>>>>[-<<<<+>>>>] top b
    [-]<<[>[>+<[-]]<[-]]>>[-<<+>>] a && b
    <<<[-]>[-<+>] store a&&b
<] endwhile

a b 0
    ^
    
a b res
0 0 ==
0 1 <
1 0 >
1 1 not possible

> a
< b
>= !a
<= !b

ab0
  ^

`>` b
<<[-]>[<+>[-]] at b

`<` a
<[-]<[->+<]>[<+>[-]] at b

`<=` !b
<<[-]+>[<[-]>[-]] at b

`>=` !a
<[-]<[->+<]+>[<[-]>[-]] at b





-=-=--=-=-=-=-=-=-=-=-=-=-=-=-=--=-=--=-=-=-=-=-=-=-=-=-=-=-=-=--=-=--=-=-=-=-=-=-=-=-=-=-=-=-=--=-=--=-=-=-=-=-=-=-=-=-=-=-=-=--=-=--=-=-=-=-=-=-=-=-=-=-=-=-=-
>>>>>> skip heap
[-]++++++ push 6
<[-]>[-<+>] store
>[-]+++++push 5
<[-]>[-<+>] store

[-]>[-]<<<[->>+>+<<<]>>>[-<<<+>>>] top a
[-]>[-]<<<[->>+>+<<<]>>>[-<<<+>>>] top b

[-]<<[>[>+<[-]]<[-]]>>[-<<+>>] a && b
<<[ while
    <<->->>
    [-]>[-]<<<<[->>>+>+<<<<]>>>>[-<<<<+>>>>] top a
    [-]>[-]<<<<[->>>+>+<<<<]>>>>[-<<<<+>>>>] top b
    [-]<<[>[>+<[-]]<[-]]>>[-<<+>>] a && b
    <<<[-]>[-<+>] store a&&b
<] endwhile
    
    
[-]<[->+>+<<]>>[-<<+>>] top b
[-] push 0
<[->-<]+>[<[-]>[-]] b==0
<<<[-]>>[-<<+>>] store a

# Ideas

Vars{id:: addr}



macros[]
put: <obj>,
Array.put: <obj>

vid.mid -> f"{vars[vid].type}.{mid}" 

struct Array{
    ptr,
    len
    
    macro put(addr, val){
        *(ptr+addr)=val;
    }
    
}

let arr: Array = {0, 8};
arr.put(4, 0)

macro put(arr, addr, val){
    *(arr+addr) = val;
}


put(arr, 4, 0);


# while

gen_cond to(cond)[  *body*  gen_cond store(cond) to(cond)]

let arr = 0;
const arr_len = 5;

let i = arr_len;
while i {
    &(arr+i) <- i;
    i = i - 1;
}

i = arr_len;
while i {
    print(&i)
}

42 @  ->  value of heap[42] 

42 69 !   -> store 69 at heap[42]


a_a_a_a0....i..
            ^
to(i) > [-] > [-] <<
a_a_a_a0....i00
            ^
[- > + to(hp-2) + to(i)]
a_a_aia0****0i0
            ^
to(hp-2)
a_a_aia0****0i0
     ^
[[-<<+>>]+<<-]+
a_aia1a0****0i0
   ^
a_a1a1a0****0i0
   ^
>[
    -<
    [->>]
    <<
a_a_a_a0****0i0
     ^
    to(i) +
    >
a_a_a_a0****1i0
             ^
    [->+to(hp-2)+to(i+1)]
a_a_aia0****00i
             ^
    >
    [-<+>]
a_a_aia0****0i0
              ^
    to(hp-2)
a_a_aia0****0i0
     ^
    [[-<<+>>]+<<-]+
a_aia1a0****0i0
   ^
a_a1a1a0****0i0
   ^
>]<[->>]<<

macro bar(a){
    a + 8
}
    .....o_o_o_o_o_0..IV
def gen_load(node: NIndex):
    assert isinstance(node, NIndex)
    global sp, head
    arr_addr = ...
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

....IV
def gen_store(node: NIndex, val_expr: Expr):
    assert isinstance(node, NStore)
    global sp, head
    res = ""
    arr_index = ...
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


    .....o_o_o_o_o_0..IV