##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Attribute Value Implementation

$Id: value.py 11744 2011-01-28 09:15:15Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.component

from memphis.form import interfaces, util


class StaticValue(object):
    """Static value adapter."""

    zope.interface.implements(interfaces.IValue)

    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.value)


class ComputedValue(object):
    """Static value adapter."""

    zope.interface.implements(interfaces.IValue)

    def __init__(self, func):
        self.func = func

    def get(self):
        return self.func(self)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.get())


class ValueFactory(object):
    """Computed value factory."""

    def __init__(self, value, valueClass, discriminators):
        self.value = value
        self.valueClass = valueClass
        self.discriminators = discriminators

    def __call__(self, *args):
        sv = self.valueClass(self.value)
        for name, value in zip(self.discriminators, args):
            setattr(sv, name, value)
        return sv


class ValueCreator(object):
    """Base class for value creator"""

    valueClass = StaticValue

    def __init__(self, discriminators):
        self.discriminators = discriminators

    def __call__(self, value, **kws):
        # Step 1: Check that the keyword argument names match the
        #         discriminators
        if set(kws).difference(set(self.discriminators)):
            raise ValueError(
                'One or more keyword arguments did not match the '
                'discriminators.')
        # Step 2: Create an attribute value factory
        factory = ValueFactory(value, self.valueClass, self.discriminators)
        # Step 3: Build the adaptation signature
        signature = []
        for disc in self.discriminators:
            spec = util.getSpecification(kws.get(disc))
            signature.append(spec)
        # Step 4: Assert the adaptation signature onto the factory
        zope.component.adapter(*signature)(factory)
        zope.interface.implementer(interfaces.IValue)(factory)
        return factory


class StaticValueCreator(ValueCreator):
    """Creates static value."""

    valueClass = StaticValue


class ComputedValueCreator(ValueCreator):
    """Creates computed value."""

    valueClass = ComputedValue
