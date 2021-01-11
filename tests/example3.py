def foo():
    # avoid circular import
    from math import sin

    # this is a comment
    return sin(1)


def bar():
    from math import cos  # noqa
    return cos(1)


def baz():
    from math import tan
    return tan(1)
