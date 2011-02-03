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
"""Error Views Implementation

$Id: error.py 11790 2011-01-31 00:41:45Z fafhrd91 $
"""
__docformat__ = "reStructuredText"
import os
import zope.component
import zope.interface
import zope.schema

from memphis import config, view

import memphis.form
from memphis.form import interfaces, util, value, pagelets

_ = interfaces.MessageFactory


ErrorViewMessage = value.StaticValueCreator(
    discriminators = ('error', 'request', 'widget', 'field', 'form', 'content')
    )

ComputedErrorViewMessage = value.ComputedValueCreator(
    discriminators = ('error', 'request', 'widget', 'field', 'form', 'content')
    )


def ErrorViewDiscriminators(
    errorView,
    error=None, request=None, widget=None, field=None, form=None, content=None):
    zope.component.adapter(
        util.getSpecification(error),
        util.getSpecification(request),
        util.getSpecification(widget),
        util.getSpecification(field),
        util.getSpecification(form),
        util.getSpecification(content))(errorView)


class ErrorViewSnippet(object):
    """Error view snippet."""
    config.adapts(
        zope.schema.ValidationError, None, None, None, None, None)
    zope.interface.implements(interfaces.IErrorViewSnippet)

    def __init__(self, error, request, widget, field, form, content):
        self.error = self.context = error
        self.request = request
        self.widget = widget
        self.field = field
        self.form = form
        self.content = content

    def createMessage(self):
        return self.error.doc()

    def update(self):
        value = zope.component.queryMultiAdapter(
            (self.context, self.request, self.widget,
             self.field, self.form, self.content),
            interfaces.IValue, name='message')
        if value is not None:
            self.message = value.get()
        else:
            self.message = self.createMessage()

    def render(self):
        return view.renderPagelet(
            pagelets.IErrorViewSnippetView, self, self.request)

    def __repr__(self):
        return '<%s for %s>' %(
            self.__class__.__name__, self.error.__class__.__name__)


class ValueErrorViewSnippet(ErrorViewSnippet):
    """An error view for ValueError."""
    config.adapts(ValueError, None, None, None, None, None)

    defaultMessage = _('The system could not process the given value.')

    def createMessage(self):
        return self.defaultMessage


class InvalidErrorViewSnippet(ErrorViewSnippet):
    """Error view snippet."""
    config.adapts(zope.interface.Invalid, None, None, None, None, None)

    def createMessage(self):
        return self.error.args[0]


class MultipleErrorViewSnippet(ErrorViewSnippet):
    """Error view snippet for multiple errors."""
    config.adapts(interfaces.IMultipleErrors, None, None, None, None, None)

    def update(self):
        pass

    def render(self):
        return ''.join([view.render() for view in self.error.errors])


class MultipleErrors(Exception):
    """An error that contains many errors"""
    zope.interface.implements(interfaces.IMultipleErrors)

    def __init__(self, errors):
        self.errors = errors
