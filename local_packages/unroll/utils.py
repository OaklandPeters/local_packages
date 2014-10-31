import itertools
import functools


def fmap(func):
    """Functional-sugar for a partial of itertools.imap.
    functools.partial(itertools.imap, func)
    See test_exotic_string_concat() for example of use.
    """
    #Not required for @unroll, but frequently useful.
    @functools.wraps(func)
    def imapper(*args, **kwargs):
        return itertools.imap(func, *args, **kwargs)
    return imapper


def invoke(outer, *args, **kwargs):
    """Used for a very direct equivalent of multiline comprehension."""
    def inner(func):
        return outer(func(*args, **kwargs))
    return inner