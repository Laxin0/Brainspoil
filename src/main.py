from lexing import Lexer, parse_prog
from generation import gen_prog
from sys import argv
from pprint import pprint

def usage():
    print("""
USAGE:
    python main.py <input.bs> [options]
          
OPTIONS:
    -f            Enable formatting in generated code.
    -o <file>     Specify output file.
                  If output file not specified, code will be printed to stdout.
    --heap=<int>  Specify heap size in elements (each element is 2 cells!).
                  By default heap is 32 elements.
    """)

def main():
    formatting = False
    print_ast = False
    heap_cap = 32
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
        elif arg == '-f':
            formatting = True
        elif arg == '--ast':
            print_ast = True
        elif arg.startswith("--heap="):
            try:
                heap_cap = int(arg[7:])
            except:
                print("Heap size must be an integer!")
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

    src = ''
    try:
        with open(input_file) as f:
            src = f.read()
    except:
        print(f"Can't open {input_file}")
        exit(1)

    l = Lexer(src, input_file)
    ast = parse_prog(l)
    if print_ast: pprint(ast)
    generated_code = gen_prog(ast, formatting=formatting, heap=heap_cap)
    if out_file == None:
        print(generated_code)
    else:
        try:
            with open(out_file, "w") as f:
                f.write(generated_code)
        except:
            print(f"Can't write into `{out_file}`.")
            exit(1)

        print(f"Code generated successfully. Written in `{out_file}`.")

    

if __name__ == "__main__":
    main()
