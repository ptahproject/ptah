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
"""Validator Implementation

$Id: validator.py 11776 2011-01-30 07:41:15Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema

from memphis import config
from memphis.form import interfaces, util


class SimpleFieldValidator(object):
    """Simple Field Validator"""
    zope.interface.implements(interfaces.IValidator)
    config.adapts(
        zope.interface.Interface,
        zope.schema.interfaces.IField)

    def __init__(self, form, field):
        self.form = form
        self.field = field

    def validate(self, value):
        """See interfaces.IValidator"""
        if value is not interfaces.NOT_CHANGED:
            return self.field.validate(value)

    def __repr__(self):
        return "<%s for %s['%s']>" %(
            self.__class__.__name__,
            self.field.interface.getName(),
            self.field.__name__)


class NoInputData(zope.interface.Invalid):
    """There was no input data because:

    - It wasn't asked for

    - It wasn't entered by the user

    - It was entered by the user, but the value entered was invalid

    This exception is part of the internal implementation of checkInvariants.

    """

class Data(object):
    zope.interface.implements(interfaces.IData)

    def __init__(self, schema, data, context):
        self._Data_data___ = data
        self._Data_schema___ = schema
        zope.interface.alsoProvides(self, schema)
        self.__context__ = context

    def __getattr__(self, name):
        schema = self._Data_schema___
        data = self._Data_data___
        try:
            field = schema[name]
        except KeyError:
            raise AttributeError(name)
        # If the found field is a method, then raise an error.
        if zope.interface.interfaces.IMethod.providedBy(field):
            raise RuntimeError("Data value is not a schema field", name)
        # Try to get the value for the field
        value = data.get(name, data)
        if value is data:
            if self.__context__ is None:
                raise NoInputData(name)
            dm = zope.component.getMultiAdapter(
                (self.__context__, field), interfaces.IDataManager)
            value = dm.get()
        # Optimization: Once we know we have a good value, set it as an
        # attribute for faster access.
        setattr(self, name, value)
        return value


class InvariantsValidator(object):
    """Simple Field Validator"""
    zope.interface.implements(interfaces.IManagerValidator)
    config.adapts(
        zope.interface.Interface,
        zope.interface.Interface,
        zope.interface.Interface,
        zope.interface.interfaces.IInterface,
        zope.interface.Interface)

    def __init__(self, context, request, view, schema, manager):
        self.context = context
        self.request = request
        self.view = view
        self.schema = schema
        self.manager = manager

    def validate(self, data):
        """See interfaces.IManagerValidator"""
        return self.validateObject(Data(self.schema, data, self.context))

    def validateObject(self, object):
        errors = []
        try:
            self.schema.validateInvariants(object, errors)
        except zope.interface.Invalid:
            pass # Just collect the errors

        return tuple([error for error in errors
                      if not isinstance(error, NoInputData)])

    def __repr__(self):
        return '<%s for %s>' %(self.__class__.__name__, self.schema.getName())
