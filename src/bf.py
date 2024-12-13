from sys import argv

TAPE_W = 5
CODE_W = 20

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
        while pc < len(self.code):
            if self.code[pc] == '+':
                self.mem[self.head] = (self.mem[self.head] + 1) % 256
            elif self.code[pc] == '-':
                self.mem[self.head] = (self.mem[self.head] - 1) % 256
            elif self.code[pc] == ',':
                self.mem[self.head] = ord(input())
            elif self.code[pc] == '.':
                print(self.mem[self.head])
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
            else:
                pass
            
            pc += 1

            if self.visual:
                print(' '.join((('_'*3) if i >= self.memcap or i < 0 else str(self.mem[i]).rjust(3, '0')) for i in range(self.head-TAPE_W, self.head+TAPE_W)))
                print(' '*(4*TAPE_W) + ' ^')
                print(''.join('_' if i >= len(self.code) or i < 0 or not(self.code[i] in '+-<>[].,') else self.code[i] for i in range(pc-CODE_W, pc+CODE_W)))
                print(' '*CODE_W + '^')
                print()
                input()

    def dumpmem(self):
        print([n for n in self.mem])

if __name__ == "__main__":
    if len(argv) < 4:
        print("Usage: python bf.py <file.bf> <tape_len (int)> <visual (bool)>")
        exit(0)
    _, file, t_len, vis_mode = argv
    code = ""
    with open(file) as f:
        code = f.read()

    is_visual = vis_mode.strip().lower() =='true'
    inter = Intepr(code, int(t_len), is_visual)
    print(f"Running bf code (Visual mode: {is_visual})...")
    inter.run()
    inter.dumpmem()
    print("Program executed")