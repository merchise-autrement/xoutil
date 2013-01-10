#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.fs.path
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Feb 16, 2012

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

import sys
from os.path import (abspath, expanduser, dirname, sep, normpath,
                     join as _orig_join)

from xoutil.functools import pow_
from xoutil.string import names


__docstring_format__ = 'rst'
__author__ = 'manu'


# TODO: import all in "from os.path import *"

rtrim = lambda path, n: pow_(dirname, n)(normalize_path(path))
rtrim.__doc__ = """Trims the last `n` components of the pathname `path`.

This basically applies `n` times the function `os.path.dirname` to `path`.

`path` is normalized before proceeding (but not tested to exists).

Example::

    >>> rtrim('~/tmp/a/b/c/d', 3)  # doctest: +ELLIPSIS
    '.../tmp/a'

    # It does not matter if `/` is at the end
    >>> rtrim('~/tmp/a/b/c/d/', 3)  # doctest: +ELLIPSIS
    '.../tmp/a'
"""


def fix_encoding(name, encoding=None):
    '''
    Fix encoding of a file system resource name.
    '''
    if not isinstance(name, str):
        if not encoding:
            encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
        fixer = name.decode if isinstance(name, bytes) else name.encode
        return fixer(encoding)
    else:
        return name


def join(base, *extras):
    '''
    Join two or more pathname components, inserting '/' as needed.
    If any component is an absolute path, all previous path components
    will be discarded.

    Normalize path (after join parts), eliminating double slashes, etc.'''
    try:
        path = _orig_join(base, *extras)
    except:
        base = fix_encoding(base)
        extras = [fix_encoding(extra) for extra in extras]
        path = _orig_join(base, *extras)
    return normpath(path)


def normalize_path(base, *extras):
    '''
    Normalize path by:

      - expanding '~' and '~user' constructions.
      - eliminating double slashes
      - converting to absolute.
    '''
    # FIXME: [med] Redundant "path" in name "xoutil.fs.path.normalize_path"
    try:
        path = _orig_join(base, *extras)
    except:
        path = join(base, *extras)
    return abspath(expanduser(path))


def get_module_path(module):
    # TODO: [med] Standardize this
    from ..compat import str_base
    mod = __import__(module) if isinstance(module, str_base) else module
    path = mod.__path__[0] if hasattr(mod, '__path__') else mod.__file__
    return abspath(dirname(path).decode('utf-8'))


def shorten_module_filename(filename):
    '''
    A filename, normally a module o package name, is shortened looking
    his head in all python path.
    '''
    path = sys.path[:]
    path.sort(lambda x, y: len(y) - len(x))
    for item in path:
        if item and filename.startswith(item):
            filename = filename[len(item):]
            if filename.startswith(sep):
                filename = filename[len(sep):]
    for item in ('__init__.py', '__init__.pyc'):
        if filename.endswith(item):
            filename = filename[:-len(item)]
            if filename.endswith(sep):
                filename = filename[:-len(sep)]
    return shorten_user(filename)


def shorten_user(filename):
    '''
    A filename is shortened looking for the (expansion) $HOME in his head and
    replacing it by '~'.

    '''
    home = expanduser('~')
    if filename.startswith(home):
        filename = _orig_join('~', filename[len(home):])
    return filename


__all__ = names('abspath', 'expanduser', 'dirname', 'sep', 'normpath',
                'fix_encoding', 'join', 'normalize_path', 'get_module_path',
                'shorten_module_filename', 'shorten_user', 'rtrim')
