from lexing import Lexer, parse_prog
from generation import gen_prog
from bf import Intepr
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: [ input | ] python log.py <file>")
        exit(0)
    _, file = sys.argv 
    src = ''
    with open(file) as f:
        src = f.read()
    l = Lexer(src, file)
    code = gen_prog(parse_prog(l), False)
    print("code:\n"+code)
    it = Intepr(code, 32, False)
    print("Execution:")
    it.run()
    print("\nMemory:")
    it.dumpmem()

if __name__ == "__main__":
    main()
