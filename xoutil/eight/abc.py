#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.eight.abc
# ---------------------------------------------------------------------
# Copyright (c) 2015-2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2015-10-18

'''Abstract Base Classes (ABCs) according to PEP 3119.

Compatibility module between Python 2 and 3.

This module defines one symbol that is defined in Python 3 as a class:

  class ABC(metaclass=ABCMeta):
      """Helper class that provides a standard way to create an ABC using
      inheritance.
      """
      pass

In our case it's defined as ``ABC = metaclass(ABCMeta)``, that is a little
tricky (see `xoutil.eight.meta.metaclass`:func`).

`abstractclassmethod` is deprecated.  Use `classmethod` with `abstractmethod`
instead.

`abstractstaticmethod` is deprecated.  Use `staticmethod` with
`abstractmethod` instead.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)


from abc import ABCMeta, abstractmethod, abstractproperty    # noqa

from xoutil.eight.mixins import helper_class

ABC = helper_class(ABCMeta)

del helper_class


# TODO: Develop tests in order to demonstrate next method runs properly in all
# Python versions.

if ABCMeta('A', (object,), {}).register(int) is not int:
    ABCMeta.__old_register__ = ABCMeta.register

    def register(cls, subclass):
        '''

        Returns the subclass, to allow usage as a class decorator.  Using this
        method, difference in Python versions from 3.3 of `register`:meth:
        method is fixed.

        '''
        ABCMeta.__old_register__(cls, subclass)
        return subclass
    register.__doc__ = ABCMeta.__old_register__.__doc__ + register.__doc__
    ABCMeta.register = register
    del register


ABCMeta.adopt = ABCMeta.register


try:
    from abc import get_cache_token
except ImportError:
    def get_cache_token():
        '''Returns the current ABC cache token.

        The token is an opaque object (supporting equality testing)
        identifying the current version of the ABC cache for virtual
        sub-classes.  The token changes with every call to ``register()`` on
        any ABC.

        '''
        return ABCMeta._abc_invalidation_counter
