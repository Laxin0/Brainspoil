# DO NOT TOUCH THIS SHIT IS UNDER DEVELOPMENT!!!

But if you want to try...

# Disclaimer
This is my project, which I do just for fun.
I am not a professional and not even advanced programmer.
English is not my native language, so there may be many mistakes (I'm sorry).

# About
My own programming language that compiles into brainfuck.
Its name *brainspoil* becouse if *brainfuck* made for fucking your brain, *brainspoil* is opposite. It should easier for your brain. Although it might be even worse.

# Download
You can just clone this repo:
```
git clone https://github.com/laxin0/Brainspoil
```

## Compilation
To compile your program written in *brainspoil* you need `main.py` file.

```
USAGE:
    python src/main.py <input.bs> [options]
          
OPTIONS:
    -f            Enable formatting in generated code.
    -o <file>     Specify output file.
                  If output file not specified, code will be printed to stdout.
    --heap=<int>  Specify heap size in elements (each element is 2 cells!).
                  By default heap is 32 elements.
```

If you didn't set `-f` flag code will be in one line without any additional symbols.
Heap size specified in elements becouse each element is 2 cells wide. It neded becouse there is no way to use the cell value as the number of steps. So you need always cary with you counter, which tell you where you are.

## Execution

The project has its own brainfuck (bf) interpreter (`src/bf.py`), but you can use your own.
```
USAGE:
    python src/bf.py <input.bf> [options]

OPTIONS:
    -v                 Enable visual mode. (Read more about it in README.md)
    -d                 Dump tape after executing program.
    --tape-len=<int>   Specify tape length. By default tape is 1024 cells.
```

You can run bf programms in visual mode.

# Visual mode
Even though it's called visual mode, it's still just text.

In visual mode you can see each step of the interpreter in the following form:
```
000 000 000 000 006 003 000 000 000 000
                     ^
>>] [-]++++++++++ [-<+>] <<[-]>[-<+>][
                    ^
```
At the top is the tape and a pointer to the current cell, at the bottom is the code and a pointer to the next command. To go to the next command, just press enter. 

## Breakpoints
There are also breakpoints. To create a break point, just put `*` in brainfuck code where you want to stop. During execution, type `b` and press `enter`. The interpreter will continue execution until the next break point. You can exit visual mode by typing `e` and `enter`.

# Brainspoil lang
## Variables and types
```
let a;  #Is is comment btw
let b = 42;
b = 'h';
```
Declare variables with `let` keyword.
There is one single type: unsigned int from 0 to 255 (That's how bf works...)
You can use char constant as number.

## Math and logic
```
let a = 2+3*(5-1);
let b = (a > 0) && !(0 <= 9);
```

Suported operations:
    math:      +, -, * (/ is not implemented yet)
    logic:     &&, ||, !
    comparing: >, >=, <, <=

Logic and comapring operation must return a boolean value, in brainspoil they returns 1 or 0.

## IO
```
print 69;    # ascii code for 'E'
print '0'+4;
let input;
read input;
```

`print` - prints character with corresponding ascii code
`read`  - reads single character from stdin and stores its code in variable

## Heap
```
let ptr = 3;
@ptr = 42;
@(ptr+1) = 69;
@0 = @1;
```

You can store values at some address in heap, and use them.
Variable, number or expression in brackets after `@` character is addres within the heap.

## Scopes
```
let a;
# can use a
{
    let b;
    # can use a and b
}
# can use a
```

You can write empty scopes.
Name shadowing is alowed:
```
let a; # global name `a`
{
    let a; # global name `.a`
    print a; # uses `.a`
}
print a; # uses `a`
```


## if else
```
let a = 1;
if a {
    print 'a';
}

if a == 0{
    print '0';
}else{
    print '1';
}
```

0 means false, anything else - true

## while
```
let i = 9;
while i{
    print '0'+i;
    i = i-1;
}
```

## macros
Procedures can be written like this
```
macro foo(a, b){
    if a > b{
        print '>';
    }else{
        print '<'; print '=";
    }
    print '\n';
}

foo(2, 3)
foo('a', 2+2);
```

Functions can be written like this:
```
macro* add(a, b){ 
    Result = a + b; 
}

let a = add(3, 5);

```

If you put `*` after `macro` you can use predefined variable `Result`.
By default `Result` is 0. It's stores return value.

If you don't use return value, compiler will warn you about that.
```
macro* foo(){Result = 42;}

foo(); # 42 was returned, but it stored on the stack and can never be used anymore.
{foo();} # If you need to do this, put in a scope
```

## Experimental
**Experimantal features that can be deprecated in future**

### strings
Just put string literal as statement for printing it:
```
"Hello world\n";
```

**You can see more examples in `tests` folder**

## How it works
Tape layout
```
o_o_o_o_o_0.........
```

`o` - Zeros. Cells for copying index counter in it. Each step couner decremented and leave tail of 1, so when it becomes 0, needed value is stored.
`0` - When head goes back it set zero in `o` cells until it encounters `0`. It means we are 'home' and we know where we are.
`.` - Just cells within the stack.

All variables are stores on the stack, all computations are done on the stack. Basically its just stack machine. 
When you write `b = a+3*4` it  copies value of `a` onto the stack, then pushes 3 and 4, makes multiplication, then addition, then stores it to `b`.