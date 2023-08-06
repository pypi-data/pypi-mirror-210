"""
Idiomatic implementation of a Python function that calculates the product of
the items from an iterable.
"""
from __future__ import annotations
from typing import Any, Optional, Iterable
import doctest
import functools
import operator

def prd(iterable: Iterable, start: Optional[Any] = 1) -> Any:
    """
    Idiomatic implementation of a product function (an analog of -- and
    complement to -- the built-in :obj:`sum` function). This function
    applies the built-in multiplication operator :obj:`operator.mul` to
    all of the items from the supplied iterable.

    >>> prd([1, 2, 3, 4])
    24
    >>> prd([2])
    2
    >>> prd([1.2, 3.4, 5.6])
    22.848
    >>> prd([])
    1

    The function is compatible with objects for which the built-in
    multiplication operator is defined.

    >>> class var(str):
    ...     def __mul__(self, other):
    ...         return self + ' * ' + other
    ...     def __rmul__(self, other):
    ...         return other + ' * ' + self
    >>> prd([var('b'), var('c'), var('d')], var('a'))
    'a * b * c * d'

    The ``start`` parameter and the elements found in the iterable can
    be of different types. It is only required that the output of the
    multiplication operation can by multiplied with the next element
    from the iterable.

    >>> prd([], 'a')
    'a'
    >>> prd([1, 2, 3], 'a')
    'aaaaaa'
    >>> prd(['a', 3], 2)
    'aaaaaa'

    If a supplied argument is missing or unsupported, a descriptive
    exceptions is raised.

    >>> prd()
    Traceback (most recent call last):
      ...
    TypeError: prd() missing 1 required positional argument: 'iterable'
    >>> prd(123)
    Traceback (most recent call last):
      ...
    TypeError: argument must support iteration
    >>> prd('abc')
    Traceback (most recent call last):
      ...
    TypeError: can't multiply sequence by non-int of type 'str'
    >>> prd([None])
    Traceback (most recent call last):
        ...
    TypeError: unsupported operand type(s) for *: 'int' and 'NoneType'
    """
    try:
        return functools.reduce(operator.mul, iterable, start)
    except TypeError as exc:
        if str(exc) == 'reduce() arg 2 must support iteration':
            raise TypeError('argument must support iteration') from None
        raise

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
