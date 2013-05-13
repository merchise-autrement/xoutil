#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.objects
#----------------------------------------------------------------------
# Copyright (c) 2013 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodríguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Feb 17, 2012

'''Several utilities for objects in general.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

from xoutil.compat import py3k as _py3k
from xoutil.deprecation import deprecated

from xoutil.names import strlist as slist
__all__ = slist('nameof', 'smart_getter', 'smart_getter_and_deleter',
                'xdir', 'fdir', 'validate_attrs', 'get_first_of',
                'get_and_del_first_of', 'smart_getattr', 'get_and_del_attr',
                'setdefaultattr', 'full_nameof', 'copy_class', 'smart_copy',
                'extract_attrs')
del slist

__docstring_format__ = 'rst'
__author__ = 'manu'

# These two functions can be use to always return True or False
_true = lambda *args, **kwargs: True
_false = lambda *args, **kwargs: False


# TODO: Deprecate and restructure all its uses
@deprecated('xoutil.names.nameof')
def nameof(target):
    '''Gets the name of an object.

    .. warning::

       *Deprecated since version 1.4.0.* Use :func:`xoutil.names.nameof`.

    '''
    from xoutil.names import nameof as wrapped
    from xoutil.compat import str_base
    if isinstance(target, str_base):
        return wrapped(target, depth=2, inner=True)
    else:
        return wrapped(target, depth=2, inner=True, typed=True)


def smart_getter(obj):
    '''Returns a smart getter for `obj`.

    If obj is Mapping, it returns the ``.get()`` method bound to the object
    `obj`. Otherwise it returns a partial of `getattr` on `obj` with default
    set to None.

    '''
    from collections import Mapping
    from xoutil.types import DictProxyType
    if isinstance(obj, (DictProxyType, Mapping)):
        return obj.get
    else:
        return lambda attr, default=None: getattr(obj, attr, default)

smart_get = deprecated(smart_getter)(smart_getter)


def smart_getter_and_deleter(obj):
    '''Returns a function that get and deletes either a key or an attribute of
    obj depending on the type of `obj`.

    If `obj` is a `collections.Mapping` it must be a
    `collections.MutableMapping`.

    '''
    from collections import Mapping, MutableMapping
    from functools import partial
    if isinstance(obj, Mapping) and not isinstance(obj, MutableMapping):
        raise TypeError('If `obj` is a Mapping it must be a MutableMapping')
    if isinstance(obj, MutableMapping):
        return partial(get_and_del_key, obj)
    else:
        return partial(get_and_del_attr, obj)

smart_get_and_del = deprecated(smart_getter_and_deleter)(smart_getter_and_deleter)


def is_private_name(name):
    '''Return if `name` is private or not.'''
    prefix = '__'
    return name.startswith(prefix) and not name.endswith(prefix)


def fix_private_name(cls, name):
    '''Correct a private name with Python conventions, return the same value if
    name is not private.

    '''
    if is_private_name(name):
        return str('_%s%s' % (cls.__name__, name))
    else:
        return name


def attrclass(obj, name):
    '''Find the definition class of an attribute specified by `name', return
    None if not found.

    If `name` is private, classes are recursed in MRO until a definition or an
    assign was made at that level.

    '''
    attrs = getattr(obj, '__dict__', {})
    if name in attrs:
        return type(obj)
    else:
        def check(cls):
            attr = fix_private_name(cls, name)
            if attr in attrs:
                return cls
            else:
                desc = getattr(cls, '__dict__', {}).get(attr)
                if desc is not None:
                    # For incompatibilities in module "types" between
                    # Python 2.x and 3.x for method types, next is a nice try
                    get = getattr(desc, '__get__', None)
                    if callable(get) and not isinstance(desc, type):
                        return cls
                    else:
                        return None
                else:
                    return None
        cls_chcks = (check(cls) for cls in type(obj).mro())
        return next((cls for cls in cls_chcks if cls is not None), None)


def fulldir(obj):
    '''Return a set with all valid attribute names defined in `obj`'''
    res = set()
    if isinstance(obj, type):
        last = None
        for cls in type.mro(obj):
            attrs = getattr(cls, '__dict__', {})
            if attrs is not last:
                for name in attrs:
                    res.add(name)
            last = attrs
    else:
        for name in getattr(obj, '__dict__', {}):
            res.add(name)
    cls = type(obj)
    if cls is not type:
        res |= set(dir(cls))
    return res


# TODO: [manu] This is only a proposal, integrate in all these functions in ...
#       order to use only one argument ``filter`` instead the use of
#       ``attr_filter`` and ``value_filter``.
#       So, ``def xdir(obj, filter=None, getter=None):``
def xdir(obj, attr_filter=None, value_filter=None, getter=None):
    '''Return all ``(attr, value)`` pairs from `obj` that ``attr_filter(attr)``
    and ``value_filter(value)`` are both True.

    :param obj: The object to be instrospected.

    :param attr_filter: *optional* A filter for attribute names.

    :param value_filter: *optional* A filter for attribute values.

    :param getter: *optional* A function with the same signature that
                   ``getattr`` to be used to get the values from `obj`.

    If neither `attr_filter` nor `value_filter` are given, all `(attr, value)`
    are generated.

    '''
    getter = getter or getattr
    attrs = dir(obj)
    if attr_filter:
        attrs = (attr for attr in attrs if attr_filter(attr))
    res = ((a, getter(obj, a)) for a in attrs)
    if value_filter:
        res = ((a, v) for a, v in res if value_filter(v))
    return res


def fdir(obj, attr_filter=None, value_filter=None, getter=None):
    '''Similar to :func:`xdir` but yields only the attributes names.'''
    return (attr for attr, _v in xdir(obj, attr_filter, value_filter, getter))


def validate_attrs(source, target, force_equals=(), force_differents=()):
    '''Makes a 'comparison' of `source` and `target` by its attributes (or
    keys).

    This function returns True if and only if both of these tests
    pass:

    - All attributes in `force_equals` are equal in `source` and `target`

    - All attributes in `force_differents` are different in `source` and
      `target`

    For instance::

        >>> class Person(object):
        ...    def __init__(self, **kwargs):
        ...        for which in kwargs:
        ...            setattr(self, which, kwargs[which])

        >>> source = Person(name='Manuel', age=33, sex='male')
        >>> target = {'name': 'Manuel', 'age': 4, 'sex': 'male'}

        >>> validate_attrs(source, target, force_equals=('sex',),
        ...                force_differents=('age',))
        True

        >>> validate_attrs(source, target, force_equals=('age',))
        False

    If both `force_equals` and `force_differents` are empty it will
    return True::

        >>> validate_attrs(source, target)
        True

    '''
    from operator import eq, ne
    res = True
    tests = ((ne, force_equals), (eq, force_differents))
    j = 0
    get_from_source = smart_getter(source)
    get_from_target = smart_getter(target)
    while res and  (j < len(tests)):
        fail, attrs = tests[j]
        i = 0
        while res and  (i < len(attrs)):
            attr = attrs[i]
            if fail(get_from_source(attr), get_from_target(attr)):
                res = False
            else:
                i += 1
        j += 1
    return res


def get_first_of(source, *keys, **kwargs):
    '''Return the first occurrence of any of the specified keys in `source`.

    If `source` is a tuple, a list, a set, or a generator; then the keys are
    searched in all the items.

    Examples:

    - To search some keys (whatever is found first) from a dict::

        >>> somedict = {"foo": "bar", "spam": "eggs"}
        >>> get_first_of(somedict, "no", "foo", "spam")
        'bar'

    - If a key/attr is not found, None is returned::

        >>> somedict = {"foo": "bar", "spam": "eggs"}
        >>> get_first_of(somedict, "eggs") is None
        True

    - Objects may be sources as well::

        >>> class Someobject(object): pass
        >>> inst = Someobject()
        >>> inst.foo = 'bar'
        >>> inst.eggs = 'spam'
        >>> get_first_of(inst, 'no', 'eggs', 'foo')
        'spam'

        >>> get_first_of(inst, 'invalid') is None
        True

    - You may pass several sources in a list, tuple or generator, and
      `get_first` will try each object at a time until it finds any of
      the key on a object; so any object that has one of the keys will
      "win"::

        >>> somedict = {"foo": "bar", "spam": "eggs"}
        >>> class Someobject(object): pass
        >>> inst = Someobject()
        >>> inst.foo = 'bar2'
        >>> inst.eggs = 'spam'
        >>> get_first_of((somedict, inst), 'eggs')
        'spam'

        >>> get_first_of((somedict, inst), 'foo')
        'bar'

        >>> get_first_of((inst, somedict), 'foo')
        'bar2'

        >>> get_first_of((inst, somedict), 'foobar') is None
        True

    You may pass a keywork argument called `default` with the value
    you want to be returned if no key is found in source::

        >>> none = object()
        >>> get_first_of((inst, somedict), 'foobar', default=none) is none
        True

    '''
    from xoutil import Unset
    from xoutil.types import is_collection
    def inner(source):
        get = smart_getter(source)
        res, i = Unset, 0
        while (res is Unset) and (i < len(keys)):
            res = get(keys[i], Unset)
            i += 1
        return res

    if is_collection(source):
        from xoutil.compat import map
        from itertools import takewhile
        res = Unset
        for item in takewhile(lambda _: res is Unset, map(inner, source)):
            if item is not Unset:
                res = item
    else:
        res = inner(source)
    return res if res is not Unset else kwargs.get('default', None)


def get_and_del_first_of(source, *keys, **kwargs):
    '''Similar to :func:`get_first_of` but uses either :func:`get_and_del_attr`
    or :func:`get_and_del_key` to get and del the first key.

    Examples::

        >>> somedict = dict(bar='bar-dict', eggs='eggs-dict')

        >>> class Foo(object): pass
        >>> foo = Foo()
        >>> foo.bar = 'bar-obj'
        >>> foo.eggs = 'eggs-obj'

        >>> get_and_del_first_of((somedict, foo), 'eggs')
        'eggs-dict'

        >>> get_and_del_first_of((somedict, foo), 'eggs')
        'eggs-obj'

        >>> get_and_del_first_of((somedict, foo), 'eggs') is None
        True

        >>> get_and_del_first_of((foo, somedict), 'bar')
        'bar-obj'

        >>> get_and_del_first_of((foo, somedict), 'bar')
        'bar-dict'

        >>> get_and_del_first_of((foo, somedict), 'bar') is None
        True

    '''
    from xoutil import Unset
    from xoutil.types import is_collection
    def inner(source):
        get = smart_getter_and_deleter(source)
        res, i = Unset, 0
        while (res is Unset) and (i < len(keys)):
            res = get(keys[i], Unset)
            i += 1
        return res

    if is_collection(source):
        res = Unset
        source = iter(source)
        probe = next(source, None)
        while res is Unset and probe:
            res = inner(probe)
            probe = next(source, None)
    else:
        res = inner(source)
    return res if res is not Unset else kwargs.get('default', None)


def smart_getattr(name, *sources, **kwargs):
    '''Gets an attr by `name` for the first source that has it::

        >>> somedict = {'foo': 'bar', 'spam': 'eggs'}
        >>> class Some(object): pass
        >>> inst = Some()
        >>> inst.foo = 'bar2'
        >>> inst.eggs = 'spam'

        >>> smart_getattr('foo', somedict, inst)
        'bar'

        >>> smart_getattr('foo', inst, somedict)
        'bar2'

        >>> from xoutil import Unset
        >>> smart_getattr('fail', somedict, inst) is Unset
        True

    You may pass all keyword arguments supported by
    :func:`get_first_of`_.

    '''
    from xoutil import Unset
    from xoutil.iterators import dict_update_new
    dict_update_new(kwargs, {'default': Unset})
    return get_first_of(sources, name, **kwargs)


def get_and_del_attr(obj, name, default=None):
    '''Looks for an attribute in the `obj` and returns its value and removes
    the attribute. If the attribute is not found, `default` is returned
    instead.

    Examples::

        >>> class Foo(object):
        ...   a = 1
        >>> foo = Foo()
        >>> foo.a = 2
        >>> get_and_del_attr(foo, 'a')
        2
        >>> get_and_del_attr(foo, 'a')
        1
        >>> get_and_del_attr(foo, 'a') is None
        True

    '''
    from xoutil import Unset
    res = getattr(obj, name, Unset)
    if res is Unset:
        res = default
    else:
        try:
            delattr(obj, name)
        except AttributeError:
            try:
                delattr(obj.__class__, name)
            except AttributeError:
                pass
    return res


def get_and_del_key(d, key, default=None):
    '''Looks for a key in the dict `d` and returns its value and removes the
    key. If the attribute is not found, `default` is returned instead.

    Examples::

        >>> foo = dict(a=1)
        >>> get_and_del_key(foo, 'a')
        1
        >>> get_and_del_key(foo, 'a') is None
        True

    '''
    from xoutil import Unset
    res = d.get(key, Unset)
    if res is Unset:
        res = default
    else:
        try:
            del d[key]
        except IndexError:
            pass
    return res


class lazy(object):
    '''Marks a value as a lazily evaluated value. See
    :func:`setdefaultattr`.

    '''
    def __init__(self, value):
        self.value = value

    def __call__(self):
        from xoutil.compat import callable
        res = self.value
        if callable(res):
            return res()
        else:
            return res


class classproperty(object):
    '''A descriptor that behaves like property for instances but for classes.

    Example of its use::

        class Foobar(object):
            @classproperty
            def getx(cls):
                return cls._x

    Class properties are always read-only, if attribute values must be setted
    or deleted, a metaclass must be defined.

    '''
    def __init__(self, fget):
        '''Create the class property descriptor.

          :param fget: is a function for getting the class attribute value

        '''
        self.__get = fget

    def __get__(self, instance, owner):
        cls = type(instance) if instance is not None else owner
        return self.__get(cls)


def setdefaultattr(obj, name, value):
    '''Sets the attribute name to value if it is not set::

        >>> class Someclass(object): pass
        >>> inst = Someclass()
        >>> setdefaultattr(inst, 'foo', 'bar')
        'bar'

        >>> inst.foo
        'bar'

        >>> inst.spam = 'egg'
        >>> setdefaultattr(inst, 'spam', 'with ham')
        'egg'

    (`New in version 1.2.1`). If you want the value to be lazily evaluated you
    may provide a lazy-lambda::

        >>> inst = Someclass()
        >>> inst.a = 1
        >>> def setting_a():
        ...    print('Evaluating!')
        ...    return 'a'

        >>> setdefaultattr(inst, 'a', lazy(setting_a))
        1

        >>> setdefaultattr(inst, 'ab', lazy(setting_a))
        Evaluating!
        'a'

    '''
    from xoutil import Unset
    res = getattr(obj, name, Unset)
    if res is Unset:
        if isinstance(value, lazy):
            value = value()
        setattr(obj, name, value)
        res = value
    return res


# TODO: Use "xoutil.names.nameof" with "full=True, inner=True, typed=True"
@deprecated('xoutil.names.nameof')
def full_nameof(target):
    '''Gets the full name of an object:

    .. warning::

       *Deprecated since 1.4.0*. Use :func:`xoutil.names.nameof` with the
       `full` argument.

    '''
    from xoutil.compat import py3k, str_base
    if isinstance(target, str_base):
        return target
    else:
        if not hasattr(target, '__name__'):
            target = type(target)
        res = target.__name__
        mod = getattr(target, '__module__', '__')
        if not mod.startswith('__') and (not py3k or mod != 'builtins'):
            res = '.'.join((mod, res))
        return res


def copy_class(cls, meta=None, ignores=None, new_attrs=None):
    '''Copies a class definition to a new class.

    The returned class will have the same name, bases and module of `cls`.

    :param meta: If None, the `type(cls)` of the class is used to build the new
                 class, otherwise this must be a *proper* metaclass.


    :param ignores: A (sequence of) string, glob-pattern, or regexp for
                    attributes names that should not be copied to new class.

                    If the strings begins with "(?" it will be considered a
                    regular expression string representation, if it does not
                    but it contains any wild-char it will be considered a
                    glob-pattern, otherwise is the exact name of the ignored
                    attribute.

                    Any ignored that is not a string **must** be an object with
                    a `match(attr)` method that must return a non-null value if
                    the the `attr` should be ignored. For instance, a regular
                    expression object.

    :param new_attrs: New attributes the class must have. These will take
                      precedence over the attributes in the original class.

    :type new_attrs: dict

    .. versionadded:: 1.4.0

    '''
    from xoutil.fs import _get_regex
    from xoutil.compat import str_base, iteritems_
    # TODO: [manu] "xoutil.fs" is more specific module than this one. So ...
    #       isn't correct to depend on it. Migrate part of "_get_regex" to a
    #       module that can be imported logically without problems from both,
    #       this and "xoutil.fs".
    from xoutil.types import MemberDescriptorType
    if not meta:
        meta = type(cls)
    if isinstance(ignores, str_base):
        ignores = (ignores, )
        ignores = tuple((_get_regex(i) if isinstance(i, str_base) else i) for i in ignores)
        ignored = lambda name: any(ignore.match(name) for ignore in ignores)
    else:
        ignored = None
    attrs = {name: value
             for name, value in iteritems_(cls.__dict__)
             if name not in ('__class__', '__mro__', '__name__', '__weakref__', '__dict__')
             # Must remove member descriptors, otherwise the old's class
             # descriptor will override those that must be created here.
             if not isinstance(value, MemberDescriptorType)
             if ignored is None or not ignored(name)}
    if new_attrs:
        attrs.update(new_attrs)
    result = meta(cls.__name__, cls.__bases__, attrs)
    return result


# Real signature is (*sources, target, filter=None) where target is a
# positional argument, and not a keyword.
# TODO: First look up "target" in keywords and then in positional arguments.
def smart_copy(*args, **kwargs):
    '''Copies the first apparition of attributes (or keys) from `sources` to
    `target`.

    :param sources: The objects from which to extract keys or attributes.

    :param target: The object to fill.

    :param defaults: Default values for the attributes to be copied as
                     explained below. Defaults to False.

    :type defaults: Either a bool, a dictionary, an iterable or a callable.

    Every `sources` and `target` are always positional arguments. There should
    be at least one source. `target` will always be the last positional
    argument, unless:

    - `defaults` is not provided as a keyword argument, and

    - there are at least 3 positional arguments and

    - the last positional argument is either None, True, False or a *function*,

    then `target` is the next-to-last positional argument and `defaults` is the
    last positional argument. Notice that passing a callable that is not a
    function is possible only with a keyword argument. If this is too
    confusing, pass `defaults` as a keyword argument.

    If `defaults` is a dictionary or an iterable then only the names provided
    by itering over `defaults` will be copied. If `defaults` is a dictionary,
    and one of its key is not found in any of the `sources`, then the value of
    the key in the dictionary is copied to `target` unless:

    - It's the value :class:`xoutil.types.Required` or an instance of Required.

    - An exception object

    - A sequence with is first value being a subclass of Exception. In which
      case :class:`xoutil.data.adapt_exception` is used.

    In these cases a KeyError is raised if the key is not found in the sources.

    If `default` is an iterable and a key is not found in any of the sources,
    None is copied to `target`.

    If `defaults` is a callable then it should receive one positional arguments
    for the current `attribute name` and several keyword arguments (we pass
    ``source``) and return either True or False if the attribute should be
    copied.

    If `defaults` is False (or None) only the attributes that do not start with
    a "_" are copied, if it's True all attributes are copied.

    When `target` is not a mapping only valid Python identifiers will be
    copied.

    Each `source` is considered a mapping if it's an instance of
    `collections.Mapping` or a DictProxyType.

    The `target` is considered a mapping if it's an instance of
    `collections.MutableMapping`.

    :returns: `target`.

    '''
    from collections import Mapping, MutableMapping
    from xoutil.compat import callable, str_base
    from xoutil.types import Unset, Required, DictProxyType
    from xoutil.types import FunctionType as function
    from xoutil.types import is_collection
    from xoutil.data import adapt_exception
    from xoutil.validators.identifiers import is_valid_identifier
    defaults = get_and_del_key(kwargs, 'defaults', default=Unset)
    if kwargs:
        raise TypeError('smart_copy does not accept a "%s" keyword argument'
                        % kwargs.keys()[0])
    if defaults is Unset and len(args) >= 3:
        args, last = args[:-1], args[-1]
        if isinstance(last, bool) or isinstance(last, function):
            defaults = last
            sources, target = args[:-1], args[-1]
        else:
            sources, target, defaults = args, last, False
    else:
        if defaults is Unset:
            defaults = False
        sources, target = args[:-1], args[-1]
    if not sources:
        raise TypeError('smart_copy requires at least one source')
    if isinstance(target, (bool, type(None), int, float, str_base)):
        raise TypeError('target should be a mutable object, not %s' %
                        type(target))
    if isinstance(target, MutableMapping):
        def setter(key, val):
            target[key] = val
    else:
        def setter(key, val):
            if is_valid_identifier(key):
                setattr(target, key, val)
    is_mapping = isinstance(defaults, Mapping)
    if is_mapping or is_collection(defaults):
        for key, val in ((key, get_first_of(sources, key, default=Unset))
                         for key in defaults):
            if val is Unset:
                if is_mapping:
                    val = defaults.get(key, None)
                else:
                    val = None
                exc = adapt_exception(val, key=key)
                if exc or val is Required or isinstance(val, Required):
                    raise KeyError(key)
            setter(key, val)
    else:
        keys = []
        for source in sources:
            get = smart_getter(source)
            if isinstance(source, (Mapping, DictProxyType)):
                items = (name for name in source)
            else:
                items = dir(source)
            for key in items:
                if defaults is False and key.startswith('_'):
                    copy = False
                elif callable(defaults):
                    copy = defaults(key, source=source)
                else:
                    copy = True
                if key not in keys:
                    keys.append(key)
                    if copy:
                        setter(key, get(key))
    return target


def extract_attrs(obj, *names, **kwargs):
    '''Returns a tuple of the `names` from an object.

    If `obj` is a Mapping, the names will be search in the keys of the `obj`;
    otherwise the names are considered regular attribute names.

    If `default` is Unset and one attribute is not found an AttributeError (or
    KeyError) is raised, otherwise the `default` is used instead.

    .. versionadded:: 1.4.0

    '''
    # TODO: Delete next:
    # from xoutil.objects import smart_getter
    get = smart_getter(obj)
    return tuple(get(attr, **kwargs) for attr in names)


if _py3k:
    from xoutil import _meta3
    __m = _meta3
else:
    from xoutil import _meta2
    __m = _meta2

metaclass = __m.metaclass


metaclass.__doc__ = '''Defines the metaclass of a class using a py3k-looking
    style.

    .. versionadded:: 1.4.1

    Usage::

       >>> class Meta(type):
       ...   pass

       # This is the same as the Py3k syntax: class Foobar(metaclass=Meta)
       >>> class Foobar(metaclass(Meta)):
       ...   pass

       >>> class Spam(dict, metaclass(Meta)):
       ...   pass

       >>> type(Spam) is Meta
       True

       >>> Spam.__bases__ == (dict, )
       True

    .. note::

       In Python 2.7, metaclasses that have colateral effects in constructors
       (combination of "__new__" and "__init__" methods), are called *twice*
       unless you use the :func:`metaclass` definition as the first argument::

          >>> class BaseMeta(type):
          ...     classes = []
          ...     def __new__(cls, name, bases, attrs):
          ...         res = super(BaseMeta, cls).__new__(cls, name, bases, attrs)
          ...         cls.classes.append(res)   # <-- side effect
          ...         return res

          >>> class Base(metaclass(BaseMeta)):
          ...     pass

          >>> class SubType(BaseMeta):
          ...     pass

          >>> class Egg(metaclass(SubType), Base):   # <-- metaclass first
          ...     pass

          >>> Egg.__base__ is Base   # <-- but the base is Base
          True

          >>> len(BaseMeta.classes) == 2
          True

          >>> class Spam(Base, metaclass(SubType)):
          ...     'Like "Egg" but it will be registered twice in Python 2.x.'

          # Fail in Python 2.x
          >>> len(BaseMeta.classes) == 3  # doctest: +SKIP
          True

          # Nevertheless the bases are ok:
          >>> Spam.__bases__ == (Base, )
          True
'''


def register_with(abc):
    '''Register a virtual `subclass` of an ABC.

    For example::

        >>> from collections import Mapping
        >>> @register_with(Mapping)
        ... class Foobar(object):
        ...     pass
        >>> issubclass(Foobar, Mapping)
            True

    '''
    def inner(subclass):
        abc.register(subclass)
        return subclass
    return inner
