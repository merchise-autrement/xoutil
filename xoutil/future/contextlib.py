#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Python Software Foundation
# All rights reserved.
#
# Most of the contents of this file were extracted from the source code of
# CPython 3.6.
#

import sys
from collections import deque
from contextlib import *  # noqa

try:
    AbstractContextManager  # noqa
except NameError:
    import abc
    from xoutil.eight.meta import metaclass

    class AbstractContextManager(metaclass(abc.ABCMeta)):

        """An abstract base class for context managers."""

        def __enter__(self):
            """Return `self` upon entering the runtime context."""
            return self

        @abc.abstractmethod
        def __exit__(self, exc_type, exc_value, traceback):
            """Raise any exception triggered within the runtime context."""
            return None

        @classmethod
        def __subclasshook__(cls, C):
            if cls is AbstractContextManager:
                return _check_methods(C, "__enter__", "__exit__")
            return NotImplemented

    # Copied from CPython 3.6 _collections_abc._check_methods
    def _check_methods(C, *methods):
        mro = C.__mro__
        for method in methods:
            for B in mro:
                if method in B.__dict__:
                    if B.__dict__[method] is None:
                        return NotImplemented
                    break
            else:
                return NotImplemented
        return True


try:
    ExitStack  # noqa
except NameError:
    # Inspired by discussions on http://bugs.python.org/issue13585
    class ExitStack(AbstractContextManager):
        """Context manager for dynamic management of a stack of exit callbacks

        For example:

            with ExitStack() as stack:
                files = [stack.enter_context(open(fname)) for fname in fnames]
                # All opened files will automatically be closed at the end of
                # the with statement, even if attempts to open files later
                # in the list raise an exception

        """
        def __init__(self):
            self._exit_callbacks = deque()

        def pop_all(self):
            "Preserve the context stack by transferring it to a new instance"
            new_stack = type(self)()
            new_stack._exit_callbacks = self._exit_callbacks
            self._exit_callbacks = deque()
            return new_stack

        def _push_cm_exit(self, cm, cm_exit):
            """Helper to correctly register callbacks to __exit__ methods"""
            def _exit_wrapper(*exc_details):
                return cm_exit(cm, *exc_details)
            _exit_wrapper.__self__ = cm
            self.push(_exit_wrapper)

        def push(self, exit):
            """Registers a callback with the standard __exit__ method signature

            Can suppress exceptions the same way __exit__ methods can.

            Also accepts any object with an __exit__ method (registering a call
            to the method instead of the object itself)
            """
            # We use an unbound method rather than a bound method to follow
            # the standard lookup behaviour for special methods
            _cb_type = type(exit)
            try:
                exit_method = _cb_type.__exit__
            except AttributeError:
                # Not a context manager, so assume its a callable
                self._exit_callbacks.append(exit)
            else:
                self._push_cm_exit(exit, exit_method)
            return exit  # Allow use as a decorator

        def callback(self, callback, *args, **kwds):
            """Registers an arbitrary callback and arguments.

            Cannot suppress exceptions.
            """
            def _exit_wrapper(exc_type, exc, tb):
                callback(*args, **kwds)
            # We changed the signature, so using @wraps is not appropriate, but
            # setting __wrapped__ may still help with introspection
            _exit_wrapper.__wrapped__ = callback
            self.push(_exit_wrapper)
            return callback  # Allow use as a decorator

        def enter_context(self, cm):
            """Enters the supplied context manager


            If successful, also pushes its __exit__ method as a callback and
            returns the result of the __enter__ method.
            """
            # We look up the special methods on the type to match the with
            # statement
            _cm_type = type(cm)
            _exit = _cm_type.__exit__
            result = _cm_type.__enter__(cm)
            self._push_cm_exit(cm, _exit)
            return result

        def close(self):
            """Immediately unwind the context stack"""
            self.__exit__(None, None, None)

        def __exit__(self, *exc_details):
            received_exc = exc_details[0] is not None

            # We manipulate the exception state so it behaves as though
            # we were actually nesting multiple with statements
            frame_exc = sys.exc_info()[1]

            def _fix_exception_context(new_exc, old_exc):
                # Context may not be correct, so find the end of the chain
                while 1:
                    exc_context = new_exc.__context__
                    if exc_context is old_exc:
                        # Context is already set correctly (see issue 20317)
                        return
                    if exc_context is None or exc_context is frame_exc:
                        break
                    new_exc = exc_context
                # Change the end of the chain to point to the exception
                # we expect it to reference
                new_exc.__context__ = old_exc

            # Callbacks are invoked in LIFO order to match the behaviour of
            # nested context managers
            suppressed_exc = False
            pending_raise = False
            while self._exit_callbacks:
                cb = self._exit_callbacks.pop()
                try:
                    if cb(*exc_details):
                        suppressed_exc = True
                        pending_raise = False
                        exc_details = (None, None, None)
                except:  # noqa
                    new_exc_details = sys.exc_info()
                    # simulate the stack of exceptions by setting the context
                    _fix_exception_context(new_exc_details[1], exc_details[1])
                    pending_raise = True
                    exc_details = new_exc_details
            if pending_raise:
                try:
                    # bare "raise exc_details[1]" replaces our carefully
                    # set-up context
                    fixed_ctx = exc_details[1].__context__
                    raise exc_details[1]
                except BaseException:
                    exc_details[1].__context__ = fixed_ctx
                    raise
            return received_exc and suppressed_exc


try:
    del nested  # noqa
except NameError:
    pass
