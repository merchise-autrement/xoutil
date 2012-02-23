#!/usr/bin/env python
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------
# untitled.py
#----------------------------------------------------------------------
# Copyright (c) 2011 Merchise H8
# All rights reserved.
#
# Author: Manuel Vázquez Acosta <mva.led@gmail.com>
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on 2011-11-08

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)


from functools import partial

from xoutil.types import is_scalar, Unset

"Several util functions for iterators"

__docstring_format__ = 'rst'
__version__ = '0.1.0'
__author__ = 'Manuel Vázquez Acosta <mva.led@gmail.com>'



def first(pred, iterable, default=None):
    '''
    Returns the first element of an iterable that matches pred.

    Examples::

        >>> first(lambda x: x > 4, range(10))
        5

        >>> first(lambda x: x < 4, range(10))
        0

    If nothing matches the default is returned::

        >>> first(lambda x: x > 100, range(10), False)
        False
    '''
    from itertools import dropwhile
    try:
        return next(dropwhile(lambda x: not pred(x), iterable))
    except StopIteration:
        return default

def get_first(iterable):
    'Returns the first element of an iterable.'
    return first(lambda x: True, iterable)


def flatten(sequence, is_scalar=is_scalar, depth=None):
    '''
    Flatten out a list by putting sublist entries in the main list. It takes
    care of everything deemed a collection (i.e, not a scalar according to the
    callabled passed in :param:`is_scalar`)::
    
        >>> tuple(flatten((1, range(2, 5), xrange(5, 10)))) # doctest: +NORMALIZE_WHITESPACE
        (1, 2, 3, 4, 5, 6, 7, 8, 9)
        
        >>> def fib(n):
        ...     if n <= 1:
        ...         return 1
        ...     else:
        ...         return fib(n-2) + fib(n-1)
        
        >>> list(flatten((range(4), (fib(n) for n in range(3))))) # doctest: +NORMALIZE_WHITESPACE
        [0, 1, 2, 3, 1, 1, 2]
        
    If :param:`depth` is None the collection is flattened recursiverly until the
    "bottom" is reached. If `depth` is an integer then the collection is 
    flattened up to that level::
    
        # depth=0 means simply not to flatten.
        >>> tuple(flatten((range(2), range(2, 4)), depth=0))     # doctest: +NORMALIZE_WHITESPACE
        ([0, 1], [2, 3])
        
        # But notice that depth=0 would not "explode" internal generators:
        >>> tuple(flatten((xrange(2), range(2, 4)), depth=0))    # doctest: +NORMALIZE_WHITESPACE
        (xrange(2), [2, 3])
        
        >>> tuple(flatten((xrange(2), range(2, 4),               # doctest: +NORMALIZE_WHITESPACE
        ...       (xrange(n) for n in range(5, 8))), depth=1))
            (0, 1, 2, 3, xrange(5), xrange(6), xrange(7))

    '''
    for item in sequence:
        if is_scalar(item):
            yield item
        elif depth == 0:
            yield item
        else:
            for subitem in flatten(item, is_scalar,
                                   depth=(depth - 1) if depth is not None
                                                     else None):
                yield subitem


def get_flat_list(sequence):
    '''Flatten out a list and return the result.'''
    return list(flatten(sequence))


def dict_update_new(target, source):
    '''
    Update values in "source" that are new (not currently present) in "target". 
    '''
    for key in source:
        if key not in target:
            target[key] = source[key]


def fake_dict_iteritems(source):
    '''
    Iterate (key, value) in a source that have defined method "keys" and
    operator "__getitem__". 
    '''
    for key in source.keys():
        yield key, source[key]


def smart_dict(defaults, *sources):
    '''
    Build a dictionary looking in sources for all keys defined in "defaults".
    Each source could be a dictionary or any other object.
    Persistence of all original objects are warranted.
    '''

    from copy import deepcopy
    from collections import Mapping
    res = {}
    for key in defaults:
        for source in sources:
            get = source.get if isinstance(source, Mapping) else partial(getattr, source)
            value = get(key, Unset)
            if (value is not Unset) and (key not in res):
                res[key] = deepcopy(value)
        if key not in res:
            res[key] = deepcopy(defaults[key])
    return res
