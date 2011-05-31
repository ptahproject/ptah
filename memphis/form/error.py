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
from memphis.form import interfaces, util, pagelets

_ = interfaces.MessageFactory


class Errors(list):
    
    def __init__(self, *args):
        super(Errors, self).__init__(*args)

        self.widgetErrors = {}

    def append(self, error):
        if interfaces.IWidgetError.providedBy(error):
            self.widgetErrors[error.name] = error

        super(Errors, self).append(error)

    def extend(self, lst):
        for error in lst:
            self.append(error)

    def getWidgetError(self, name, default=None):
        return self.widgetErrors.get(name, default)


class WidgetError(object):
    zope.interface.implements(interfaces.IWidgetError)

    def __init__(self, name, error):
        self.name = name
        self.error = error


class CustomValidationError(zope.schema.ValidationError):
    """ custom validation error """

    def __init__(self, msg):
        self.__doc__ = msg

    def doc(self):
        return self.__doc__


class ErrorViewSnippet(object):
    """Error view snippet."""
    config.adapts(zope.schema.ValidationError, None)
    zope.interface.implements(interfaces.IErrorViewSnippet)

    def __init__(self, error, request):
        self.error = self.context = error
        self.request = request

    def createMessage(self):
        return self.error.doc()

    def update(self, widget=None):
        self.widget = widget
        self.message = self.createMessage()

    def render(self):
        return view.renderPagelet(
            pagelets.IErrorViewSnippetView, self, self.request)

    def __repr__(self):
        return '<%s for %s>' %(
            self.__class__.__name__, self.error.__class__.__name__)


class StrErrorViewSnippet(ErrorViewSnippet):

    def createMessage(self):
        return self.error


class ValueErrorViewSnippet(ErrorViewSnippet):
    """An error view for ValueError."""
    config.adapts(ValueError, None)

    defaultMessage = _('The system could not process the given value.')

    def createMessage(self):
        return self.defaultMessage


class InvalidErrorViewSnippet(ErrorViewSnippet):
    """Error view snippet."""
    config.adapts(zope.interface.Invalid, None)

    def createMessage(self):
        return self.error.args[0]


class MultipleErrorViewSnippet(ErrorViewSnippet):
    """Error view snippet for multiple errors."""
    config.adapts(interfaces.IMultipleErrors, None)

    def update(self):
        pass

    def render(self):
        return u''.join(view.render() for view in self.error.errors)


class MultipleErrors(Exception):
    """An error that contains many errors"""
    zope.interface.implements(interfaces.IMultipleErrors)

    def __init__(self, errors):
        self.errors = errors
