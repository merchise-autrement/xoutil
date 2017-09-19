#!/USSR/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.dim.base
# ---------------------------------------------------------------------
# Copyright (c) 2017 Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2017-09-14

'''The standard `physical quantities`_.

.. _physical quantities: https://en.wikipedia.org/wiki/International_System_of_Quantities#Base_quantities

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        absolute_import as _py3_abs_import)

from .meta import (
    QuantityType,
    UNIT,
)


def kilo(v):
    return 1000 * v


def centi(v):
    return v / 100


def milli(v):
    return v / 1000


def micro(v):
    return v / 1000000


def nano(v):
    return v / (10**9)


@QuantityType.new()
class Length(object):
    metre = UNIT
    kilometer = km = kilo(metre)
    centimeter = cm = centi(metre)
    millimeter = mm = milli(metre)
    nanometer = nm = nano(metre)


metre = m = Length.m = Length.metre
L = Length


@QuantityType.new
class Time(object):
    second = UNIT
    millisecond = ms = milli(second)
    nanosecond = ns = nano(second)
    minute = second * 60
    hour = minute * 60


second = s = Time.s = Time.second
T = Time


@QuantityType.new(unit_aliases=('kg', ))
class Mass(object):
    kilogram = UNIT
    gram = kilogram / 1000


kilogram = kg = Mass.kg
M = Mass


@QuantityType.new(unit_aliases='A')
class ElectricCurrent(object):
    ampere = UNIT
    milliampere = milli(ampere)


A = ampere = ElectricCurrent.A
I = ElectricCurrent


@QuantityType.new(unit_aliases='K')
class Temperature(object):
    kelvin = UNIT

    @classmethod
    def from_celcius(cls, val):
        'Convert `val` ºC to K'
        return (val + 273.15) * cls.kelvin

    @classmethod
    def from_fahrenheit(cls, val):
        'Convert `val` ºF to K'
        return (val + 459.67) * (5 / 9) * cls.kelvin


K = kelvin = Temperature.K
O = Temperature   # The actual symbol would be the capital letter Theta: Θ


@QuantityType.new(unit_alias='mol')
class Substance(object):
    mole = UNIT


mole = mol = Substance.mol
N = Substance


@QuantityType.new
class Luminosity(object):
    candela = UNIT


J = Luminosity


# Derived quantities
Area = L**2
Volume = L**3
Volume.metre_cubic = Volume._unit_
Volume._unitname_ = 'metre_cubic'

Frequency = T**-1
Frequency.Hz = Frequency._unit_

Force = L * M / T**2
assert hasattr(Force, 'metre_kilogram_per_second_squared')
assert Force == L * M * T**-2
Force.Newton = Force.N = Force._unit_

Presure = M / L / T**2
assert hasattr(Presure, 'kilogram_per_metre_per_second_squared')
assert Presure == L**-1 * M * T**-2, 'as defined in Wikipedia'
Presure.Pascal = Presure.Pa = Presure._unit_

Velocity = L / T
Acceleration = L / T**2