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
"""Widget Framework Implementation"""
import zope.interface
import zope.schema
from zope.interface.common import mapping

from memphis import config
from memphis.form import interfaces

_marker = []


class AttributeField(object):
    """Attribute field."""
    zope.interface.implements(interfaces.IDataManager)
    config.adapts(zope.interface.Interface, zope.schema.interfaces.IField)

    def __init__(self, context, field):
        self.context = context
        self.field = field

    @property
    def adapted_context(self):
        # get the right adapter or context
        context = self.context
        if self.field.interface is not None:
            context = self.field.interface(context)
        return context

    def get(self):
        return self.field.get(self.adapted_context)

    def query(self, default=interfaces.NO_VALUE):
        try:
            return self.get()
        except AttributeError:
            return default

    def set(self, value):
        context = self.adapted_context
        field = self.field.bind(context)
        field.set(context, value)


class DictionaryField(object):
    """Dictionary field.

    NOTE: Even though, this data manager allows nearly all kinds of
    mappings, by default it is only registered for dict, because it
    would otherwise get picked up in undesired scenarios. If you want
    to it use for another mapping, register the appropriate adapter in
    your application.

    """
    zope.interface.implements(interfaces.IDataManager)
    config.adapts(dict, zope.schema.interfaces.IField)

    _allowed_data_classes = (dict,)

    def __init__(self, data, field):
        if (not isinstance(data, self._allowed_data_classes) and
            not mapping.IMapping.providedBy(data)):
            raise ValueError("Data are not a dictionary: %s" %type(data))
        self.data = data
        self.field = field

    def get(self):
        """See z3c.form.interfaces.IDataManager"""
        value = self.data.get(self.field.__name__, _marker)
        if value is _marker:
            raise AttributeError
        return value

    def query(self, default=interfaces.NO_VALUE):
        """See z3c.form.interfaces.IDataManager"""
        return self.data.get(self.field.__name__, default)

    def set(self, value):
        """See z3c.form.interfaces.IDataManager"""
        if self.field.readonly:
            raise TypeError("Can't set values on read-only fields name=%s"
                            % self.field.__name__)
        self.data[self.field.__name__] = value
