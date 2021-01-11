from math import cos
from math import tan


def bar():
    return cos(1)


def baz():
    from .example1 import foo
    return tan(1)
