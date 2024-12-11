from lexing import Lexer, parse_prog
from generation import gen_prog

def main():
    src = ''
    with open("code.bs") as f:
        src = f.read()
    l = Lexer(src, "code.bs")
    with open("out.bf", "w") as f:
        f.write(gen_prog(parse_prog(l)))
    print("Code generated")

if __name__ == "__main__":
    main()
