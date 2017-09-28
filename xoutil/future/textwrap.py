# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.future.textwrap
# ---------------------------------------------------------------------
# Copyright (c) 2014-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the Python Software Licence as of Python 3.3.
#
# Created on 2014-02-26
# Migrated to 'future' on 2016-09-18

'''Text wrapping and filling.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from textwrap import *    # noqa
import textwrap as _stdlib
from textwrap import __all__    # noqa
__all__ = list(__all__)

from xoutil.future import _past    # noqa
_past.dissuade()
del _past


def dedent(text, skip_firstline=False):
    r'''Remove any common leading whitespace from every line in text.

    This can be used to make triple-quoted strings line up with the left edge
    of the display, while still presenting them in the source code in indented
    form.

    Note that tabs and spaces are both treated as whitespace, but they are not
    equal: the lines ``"    hello"`` and ``"\thello"`` are considered to have
    no common leading whitespace.

    If `skip_firstline` is True, the first line is separated from the rest of
    the body.  This helps with docstrings that follow `257`:pep:.

    .. warning:: The `skip_firstline` argument is missing in standard library.

    '''
    if skip_firstline:
        parts = text.split('\n', 1)
        if len(parts) > 1:
            subject, body = parts
        else:
            subject, body = parts[0], ''
        result = _stdlib.dedent(subject)
        if body:
            result += '\n' + _stdlib.dedent(body)
    else:
        result = _stdlib.dedent(text)
    return result


try:
    indent
except NameError:
    # The following is Copyright (c) of the Python Software Foundation.
    def indent(text, prefix, predicate=None):
        """Adds 'prefix' to the beginning of selected lines in 'text'.

        If 'predicate' is provided, 'prefix' will only be added to the lines
        where 'predicate(line)' is True. If 'predicate' is not provided, it
        will default to adding 'prefix' to all non-empty lines that do not
        consist solely of whitespace characters.

        .. note:: Backported from Python 3.3.  In Python 3.3 this is an alias.

        """
        if predicate is None:
            def predicate(line):
                return line.strip()

        def prefixed_lines():
            for line in text.splitlines(True):
                yield (prefix + line if predicate(line) else line)
        return ''.join(prefixed_lines())

    __all__ = list(__all__)
    __all__.append('indent')