# Disclaimer
This is my project, which I do just for fun.
I am not a professional and not even advanced programmer.
English is not my native language, so there may be many mistakes (I'm sorry).

# About
My own programming language that compiles into brainfuck.
Its name *brainspoil* becouse if *brainfuck* made for fucking your brain, *brainspoil* is opposite.
It should be easier for your brain. Although it might be even worse.

## Brainspoil compilation
To compile your program written in *brainspoil* to brainfck you need `bs`.

```
USAGE:
    python src/main.py <input.bs> [options]
          
OPTIONS:
    -f            Enable formatting in generated code.
    -o <file>     Specify output file.
                  If output file not specified, code will be printed to stdout.
```

If you didn't set `-f` flag code will be in one line without any additional symbols. (Experimental feature)

## Brainfck 

The project has its own brainfck interpreter and compiler (`src/bf.py`), but you can use your own.
```
USAGE:
    bf <input.bf> [options] 

OPTIONS:
    -len=<int>    Specify tape length. By default tape is 1024 cells.
    -v            Enable visual mode. (For intrpretation) (Read more about it in README.md)
    -d            Dump tape after executing program. (For interpretation)
    -c            Compile program to fasm assembly.
    -o            Specify output file name. (For compilation)
    -h            Print this message.
```

## Examples

```
./bs examples/hello_world.bs -o hello.bf
./bf hello.bf
```

```
./bs examples/rule110.bs -o rule.bf
./bf rule.bf -c -o rule.s
fasm rule.s
./out
```

# Visual mode
You can run bf programms in visual mode.
Even though it's called visual mode, it's still just text.

In visual mode you can see each step of the interpreter in the following form:
```
004 005 006 007 008 009 010 011 012 013
000 000 000 000 006 003 000 000 000 000
                     ^
>>] [-]++++++++++ [-<+>] <<[-]>[-<+>][
                    ^
```
At the top is the tape and a pointer to the current cell and its address within the tape,
at the bottom is the code and a pointer to the next command. To go to the next command, just press enter. 

## Breakpoints
There are also breakpoints. To create a break point, just put `*` in brainfuck code where you want to stop.
During execution, type `b` and press `enter`. The interpreter will continue execution until the next break point.
You can exit visual mode by typing `e` and `enter`.

# Brainspoil lang
## Variables and types
```
let a;  # Comment like in python
let b = 42;
b = 'h';
```
Declare variables with `let` keyword.
There is one single type: unsigned int from 0 to 255 (That's how bf works...)
You can use char constant as number.

## Constants
```
const C = 42;
```
Сonstants are not allocated on the stack, its value known at compile time

## Math and logic
```
let a = 2+3*(5-1);
let b = (a > 0) && !(0 <= 9);
```

Suported operations:
    math:      +, -, * (/ and % are not implemented yet)
    logic:     &&, ||, !
    comparing: >, >=, <, <=

Logic and comapring operation must return a boolean value, in brainspoil they returns 1 or 0.

## IO
```
print 69;    # ascii code for 'E'
print '0'+4;

let input;
read input;
print input;
```

`print` - prints character with corresponding ascii code
`read`  - reads single character from stdin and stores its code in variable

## Strings
Just put string literal as statement for printing it:
```
"Hello world\n";
```

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

There is some problems with checking if name used and by who.
But when I tested these things it worked (kinda)

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

It is more optimal to count backwards because comperasing is a heavy operation.

## Arrays
```
const SIZE = 5;

arr array1[10];
arr array2[SIZE];
```
The size of the array is specified in the number of elements? but actual size in cells are 2*n+1+2
The size of an array must be less then 256 and size must be known at compile time
because of limitaion of brainfck and my brain.

```
arr array[10];
array[0] = 4;
let first = array[0];
```

Array using is a heavy operation.

>[!bug]
>If the index goes beyond the bounds of the array, undefined behavior will occur!

## macros
Procedures can be written like this
```
macro foo(a, b){
    if a > b{
        ">";
    }else{
        "<=";
    }
    "\n"
}

foo(2, 3)
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

## Passing by reference
Macros can accept variables and array by reference.
The symbol `&` must be present both in definition and in use.

```
macro mut(&a, b){
    a = 4;
    b = 4;
}

let a = 2; let b = 3;
mut(&a, b); 
# 'a' was mutated, 'b' stays the same. 
```

Arrays can be passed only by reference
```
macro print_last(&array, size){
    print array[size-1];
}
```

**You can see more examples in `exapmles` folder**

## How it works
All variables are stores on the stack, all computations are done on the stack. Basically its just stack machine. 
When you write `b = a+3*4` it  copies value of `a` onto the stack, then pushes 3 and 4, makes multiplication, then addition, then stores it to `b`.

The most confusing part is arrays.
Array layout:
```
_x_a_a_a_a_a0
```
Where
`a`  - Actual values inside of the array
`_`  - Zeros. Cells for copying index counter in it. Each step couner decremented and leave tail of 1, so when it becomes 0, needed value is stored one byte right.
`0`  - When head goes back it erases tail of 1 in `_` cells until it encounters `0`. It means we are 'home' and we know where we are.
`_x` - End section needed for copying last element when needed. (The value copyes into next left `_` cell and ontop of the stack and after moves back)
