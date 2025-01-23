from dataclasses import *


def print_ast(node, indent):
    #print(node.__class__.__name__)
    for name, field in node.__dataclass_fields__.items():
        print((" "*indent)+f"└{name}: {field.type.__name__}")
        if is_dataclass(node.__getattribute__(name)):
            print_ast(node.__getattribute__(name), 1)

@dataclass
class Bar():
    ab: bool
    bb: int

@dataclass
class Foo():
    a: str
    bar: Bar

bar = Bar(True, 42)
foo = Foo("bratuha", bar)
#print(bar)
print_ast(foo, 0)