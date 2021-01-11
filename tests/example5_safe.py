from math import tan


def bar():
    from math import cos
    return cos(1)


def baz():
    from .example1 import foo
    return tan(1)
