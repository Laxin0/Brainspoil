from sys import argv
from math import log10, ceil
TAPE_W = 5
CODE_W = 20
FILL_C = ' '
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

#      0   1   2   3   4   5   6   7   8   9  
# 000_ 000 000 000 000 000 000 000 000 000 000
# 001_ 000 000 000 000 000 000 000 000 000 000
# 002_ 000 000 000 000 000 000 000 000 000 000


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
    python bf.py <input.bf> [options]

OPTIONS:
    -v                 Enable visual mode. (Read more about it in README.md)
    -d                 Dump tape after executing program.
    --tape-len=<int>   Specify tape length. By default tape is 1024 cells.
""")

if __name__ == "__main__":
    input_file = None
    tape_len = 1024
    visual = False
    dump_mem = False
    args = argv[1:]
    while len(args) > 0:
        arg = args.pop(0)
        if arg == '-d':
            dump_mem = True
        elif arg == '-v':
            visual = True
        elif arg.startswith("--tape-len="):
            try:
                tape_len = int(arg[11:])
            except:
                print("Tape length must be an integer!")
                exit(1)
        elif input_file == None:
            input_file = arg
        else:
                print("Invalid arguments!")
                usage()
                exit(1)
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

    inter = Intepr(code, tape_len, visual)
    print(f"Running bf code (Visual mode: {visual})...")
    inter.run()
    if dump_mem: inter.dumpmem()
    print("Program executed.")