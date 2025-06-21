#!/usr/bin/python3

from sys import argv
from math import ceil
from dataclasses import dataclass

TAPE_W = 5
CODE_W = 20
FILL_C = ' '

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

def compilebf(src: str, tape_len, out_file):

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
        out.write(f"tape: times {tape_len} db 0\n")

# Interpretation

class Intepr():
    
    head: int
    code: str
    mem: bytearray
    memcap: int
    visial: bool

    def __init__(self, code, memcap=1024, visual=False):
        self.code = code
        self.memcap = memcap
        self.visual = visual

    def run(self):
        pc = 0
        self.mem = bytearray(self.memcap)
        self.head = 0
        breakp = True
        while pc < len(self.code):
            if self.code[pc] == '+':
                self.mem[self.head] = (self.mem[self.head] + 1) % 256
            elif self.code[pc] == '-':
                self.mem[self.head] = (self.mem[self.head] - 1) % 256
            elif self.code[pc] == ',':
                self.mem[self.head] = ord(input())
            elif self.code[pc] == '.':
                print(chr(self.mem[self.head]), end='')
            elif self.code[pc] == '>':
                self.head += 1
            elif self.code[pc] == '<':
                self.head -= 1
            elif self.code[pc] == '[':
                if self.mem[self.head] == 0:
                    stack = 1
                    while stack > 0:
                        pc += 1
                        if self.code[pc] == '[':
                            stack += 1
                        if self.code[pc] == ']':
                            stack -= 1
                    
            elif self.code[pc] == ']':
                if self.mem[self.head] != 0:
                    stack = 1
                    while stack > 0:
                        pc -= 1
                        if self.code[pc] == '[':
                            stack -= 1
                        if self.code[pc] == ']':
                            stack += 1
            elif self.code[pc] == '*':
                breakp = True
            else:
                pass #TODO: maybe skip(continue)
            
            pc += 1

            if self.visual and breakp: #TODO: rewrite this 
                print(' '.join((str(i).rjust(3, '0')) for i in range(self.head-TAPE_W, self.head+TAPE_W)))
                print(' '.join(((FILL_C*3) if i >= self.memcap or i < 0 else str(self.mem[i]).rjust(3, '0')) for i in range(self.head-TAPE_W, self.head+TAPE_W)))
                print(' '*(4*TAPE_W) + ' ^')
                print(''.join(FILL_C if i >= len(self.code) or i < 0 or self.code[i].isspace() else self.code[i] for i in range(pc-CODE_W, pc+CODE_W)))
                print(' '*CODE_W + '^')
                print()
                inp = input() #TODO: make more interactions {'a': 66, 'b': 67, 'foo.a': 68, 'foo.b': 69, 'foo.c': 70, 'foo.d': 71}
                if inp == 'b':
                    breakp = False
                elif inp == 'e':
                    self.visual = False


    def dumpmem(self):
        addr_len = 0
        cap = self.memcap
        while cap > 0:
            cap //= 10
            addr_len += 1

        print('      0   1   2   3   4   5   6   7   8   9')
        for r in range(ceil(self.memcap/10)):   
            row = ''
            current = False
            for c in range(10):
                i = r*10+c
                if i >= self.memcap: break
                row += str(self.mem[i]).rjust(3, '0')+' '
                if self.mem[i] != 0: current = True
            
            if current:
                print(f'{r}'.rjust(addr_len-1, '0')+'0: ', end='')
                print(row)
            current = False

def usage():
    print ("""
USAGE:
    bf <input.bf> [options] 

OPTIONS:
    -len=<int>    Specify tape length. By default tape is 1024 cells.
    -v            Enable visual mode. (For intrpretation) (Read more about it in README.md)
    -d            Dump tape after executing program. (For interpretation)
    -c            Compile program to fasm assembly.
    -o            Specify output file name. (For compilation)
    -h            Print this message.
    
""")

def interpret(code, tape_len, visual, dump_mem):
    inter = Intepr(code, tape_len, visual)
    print(f"Running bf code (Visual mode: {visual})...")
    inter.run()
    if dump_mem: inter.dumpmem()

if __name__ == "__main__":
    input_file = None
    output_file = None
    compile_mode = False
    tape_len = 1024
    visual = False
    dump_mem = False
    args = argv[1:]
    while len(args) > 0:
        arg = args.pop(0)
        if arg.startswith('-'):
            if arg == '-d':
                dump_mem = True
            if arg == '-c':
                compile_mode = True
            elif arg == '-v':
                visual = True
            elif arg == '-h':
                usage()
                exit(0)
            elif arg.startswith("-len="):
                try:
                    tape_len = int(arg[5:])
                except:
                    print("Tape length must be an integer!")
                    exit(1)
            elif arg == '-o':
                if len(args) == 0:
                    print("No output file name was provided!")
                    exit(1)
                out_file = args.pop(0)

            elif input_file == None:
                input_file = arg
            else:
                    print(f"Invalid option `{arg}`!")
                    usage()
                    exit(1)
        else:
            input_file = input_file or arg

        if input_file == None:
            print("No input file was provided!")
            usage()
            exit(1)
        
    code = ""
    try:
        with open(input_file) as f:
            code = f.read()
    except:
        print(f"Can't open `{input_file}`.")
        exit(1)

    if (compile_mode):
        if output_file == None:
            while len(input_file) >= 1 and input_file[-1] != '/':
                input_file = input_file[:-1]
            output_file = input_file+'out.s'
        compilebf(code, tape_len, output_file)
        print("Assembly generated.")
    else:
        interpret(code, tape_len, visual, dump_mem)
        print("Program executed.")