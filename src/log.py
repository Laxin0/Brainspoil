from lexing import Lexer, parse_prog
from generation import gen_prog
from bf import Intepr
import sys
from pprint import pprint

def main():
    if len(sys.argv) < 2:
        print("Usage: [ input | ] python log.py <file>")
        exit(0)
    _, file, *s = sys.argv 
    src = ''
    with open(file) as f:
        src = f.read()
    l = Lexer(src, file)
    ast = parse_prog(l)
    if len(sys.argv) > 2: pprint(ast)
    code = gen_prog(ast, False)
    print("code:\n"+code)
    it = Intepr(code, 128, False)
    print("Execution:")
    it.run()
    print("\nMemory:")
    it.dumpmem()

if __name__ == "__main__":
    main()
