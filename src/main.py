from lexing import Lexer, parse_prog
from generation import gen_prog
from sys import argv

def main():
    if len(argv) < 3:
        print("Usage: python <src_code.bs> <out.bf>")
        exit(0)
    _, in_file, out_file = argv 
    #in_file, out_file = "code.bs", "build/out.bf"
    src = ''
    with open(in_file) as f:
        src = f.read()
    print("Generating bf code...")
    l = Lexer(src, in_file)
    with open(out_file, "w") as f:
        f.write(gen_prog(parse_prog(l), False))
    print("Code generated successfully.")

if __name__ == "__main__":
    main()
