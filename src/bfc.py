#!/usr/bin/python3

import subprocess
from dataclasses import dataclass
from sys import argv

def separate(s: str):
    if len(s) < 1: return []
    l = [s[0]]
    for i in s[1:]:
        if l[-1][0] == i and i not in "[],.":
            l[-1] += i
        else:
            l.append(i)
    return l

@dataclass
class Op():
    type:  str
    count: int

    def __str__(self) -> str:
        return f"{self.count}{self.type}"

def gen_ops(l: list[str]):
    ops = []
    for i in l:
        ops.append(Op(i[0], len(i)))
    return ops

def usage():
    print("""
USAGE:
    bfc <input.bs> [options]
          
OPTIONS:
    -o <file>     Specify output file.
""")

def main():
    input_file = None
    out_file = None

    args = argv[1:]

    while len(args) > 0:
        arg = args.pop(0)
        if arg == '-o':
            if len(args) == 0:
                print("No output file name was provided!")
                exit(1)
            out_file = args.pop(0)
        elif input_file == None:
            input_file = arg
        else:
                print("Invalid arguments!")
                usage()
                exit(1)

    src: str
    if out_file == None: out_file = "out.s"
    if input_file == None:
        print("No input file name was provided!")
        exit(1)

    with open(input_file) as in_file:
        src = in_file.read()

    src = src.replace("[-]", '0')
    src = "".join(filter((lambda x: x in '+-<>[],.0'), src))
    ops = gen_ops(separate(src))

    with open(out_file, "w") as out:
        lc = 0
        ls = []
        out.write("FORMAT ELF64 EXECUTABLE\n")
        out.write("entry start\n")
        out.write("start:\n")
        out.write("    mov rbx, 0\n")
        for op in ops:
            match (op.type, op.count):
                case '+', c:
                    out.write(f"    add BYTE [tape+rbx], {c}\n")
                case '-', c:
                    out.write(f"    sub BYTE [tape+rbx], {c}\n")
                case '<', c:
                    out.write(f"    sub rbx, {c}\n")
                case '>', c:
                    out.write(f"    add rbx, {c}\n")
                case '[', _:
                    out.write( "    cmp BYTE [tape+rbx], 0\n")
                    out.write(f".again{lc}:\n")
                    out.write(f"    je .over{lc}\n")
                    ls.append(lc)
                    lc += 1
                case ']', _:
                    ln = ls.pop()
                    out.write( "    cmp BYTE [tape+rbx], 0\n")
                    out.write(f"    jne .again{ln}\n")
                    out.write(f".over{ln}:\n")
                case '.', _:
                    out.write("    mov rax, 1\n")
                    out.write("    mov rdi, 1\n")
                    out.write("    lea rsi, BYTE [tape+rbx]\n")
                    out.write("    mov rdx, 1\n")
                    out.write("    syscall\n")
                case ',', _:
                    out.write("    mov rax, 0\n")
                    out.write("    mov rdi, 0\n")
                    out.write("    lea rsi, BYTE [tape+rbx]\n")
                    out.write("    mov rdx, 1\n")
                    out.write("    syscall\n")
                case '0', _:
                    out.write("    mov BYTE [tape+rbx], 0\n")

        out.write("    mov rax, 60\n")
        out.write("    mov rdi, 0\n")
        out.write("    syscall\n")
        out.write("tape: times 2048 db 0\n")
